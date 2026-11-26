"""Lee y escribe copias de seguridad de clientes en JSON y CSV."""

import csv
import json
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from io import StringIO
from typing import Any
from unicodedata import category

from pydantic import ValidationError

from app.schemas.client_backup_schema import (
    CSV_BACKUP_SCHEMA_VERSION,
    JSON_BACKUP_SCHEMA_VERSION,
    PROJECT_RESOURCE_COLLECTIONS,
    BackupRecord,
    ClientBackup,
)


_CSV_FIELDS_BY_ENTITY = {
    "client": ("name", "cif", "phone", "is_active"),
    "tag": ("tag_type", "brand", "model", "mac", "ip"),
    "project": ("name", "description", "is_active"),
    "environment": ("type", "url"),
    "repository": ("type", "url"),
    "domain": ("url",),
    "link": ("title", "url"),
    "service": ("name",),
    "command": ("name", "instruction"),
    "note": ("description", "content"),
}


def _get_csv_data_columns() -> tuple[str, ...]:
    # Reúne los campos de cada entidad en orden y sin repetir columnas.
    column_names: list[str] = []
    for field_names in _CSV_FIELDS_BY_ENTITY.values():
        for field_name in field_names:
            if field_name not in column_names:
                column_names.append(field_name)

    return tuple(column_names)


_CSV_DATA_COLUMNS = _get_csv_data_columns()
_CSV_HEADER = (
    "schema_version",
    "entity",
    "id",
    "parent_id",
    *_CSV_DATA_COLUMNS,
    "collection_counts",
)
_CSV_NULL_MARKER = r"\N"
_CSV_TEXT_PREFIX = "\\"
_CSV_START_CHARS_THAT_NEED_PREFIX = ("\\", "'", "=", "+", "-", "@", "＝", "＋", "－", "＠")


class BackupFormatError(ValueError):
    code: str
    location: str | None
    validation_details: dict[str, Any]


def _make_backup_format_error(
    message: str,
    code: str = "invalid_data",
    location: str | None = None,
) -> BackupFormatError:
    error = BackupFormatError(message)
    error.code = code
    error.location = location
    error.validation_details = {}
    return error


@dataclass
class _CsvRecord:
    """Una fila del CSV con sus campos de datos ya convertidos."""
    entity: str
    parent_id: int | None
    fields: dict[str, Any]
    line_number: int
    collection_counts_text: str


def _validate_backup_model(backup_data: Any) -> ClientBackup:
    try:
        return ClientBackup.model_validate(backup_data)

    except ValidationError as validation_error:
        errors = validation_error.errors(include_url=False)

        first_error = errors[0]
        message = first_error["msg"]
        field_path = first_error["loc"]

        # Convierte cada parte de la ruta a texto. Por ejemplo, 0 pasa a "0".
        path_parts: list[str] = []
        for part in field_path:
            path_parts.append(str(part))

        # Une las partes para obtener algo como projects.0.notes.1.content.
        path_text = ".".join(path_parts)
        error_location = None
        if path_text != "":
            error_location = path_text

        backup_error = _make_backup_format_error(message, location=error_location)
        for detail_name in ("input", "ctx"):
            if detail_name in first_error:
                backup_error.validation_details[detail_name] = first_error[detail_name]

        raise backup_error from validation_error


def to_json(backup: ClientBackup) -> bytes:
    """Genera el archivo JSON de la copia en UTF-8."""
    json_text = backup.model_dump_json(indent=2)
    return json_text.encode("utf-8")


def from_json(content: bytes) -> ClientBackup:
    
    backup_data = _read_json_data(content)
    client_backup = _validate_backup_model(backup_data)

    _check_unique_ids(client_backup.tags, "tags", ids=set())
    _check_unique_ids(client_backup.projects, "projects", ids=set())

    # Los recursos del mismo tipo deben tener identificadores únicos entre proyectos.
    for collection_name in PROJECT_RESOURCE_COLLECTIONS.values():
        ids: set[int] = set()
        for project in client_backup.projects:
            resources = getattr(project, collection_name)
            _check_unique_ids(resources, collection_name, ids)

    return client_backup


def _read_json_data(content: bytes) -> Any:
    try:
        # Convierte los bytes del archivo en texto.
        json_text = content.decode("utf-8-sig")

        # Lee el texto JSON y lo convierte en datos de Python.
        json_data = json.loads(
            json_text,
            object_pairs_hook=_read_json_object,     # Comprueba si hay claves repetidas.
            parse_constant=_reject_non_json_number,  # Rechaza numeros no permitidos
        )

        # 3. Devuelve los datos leídos.
        return json_data

    except BackupFormatError:
        raise

    except json.JSONDecodeError as error:
        location = f"línea {error.lineno}, columna {error.colno}"
        raise _make_backup_format_error(
            "El JSON tiene sintaxis inválida.",
            code="invalid_syntax",
            location=location,
        ) from error

    except (ValueError, RecursionError) as error:
        raise _make_backup_format_error(
            "El JSON es inválido.",
            code="invalid_syntax",
        ) from error


def _read_json_object(json_keys_and_values: list[tuple[str, Any]]) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for field_name, value in json_keys_and_values:
        if field_name in fields:
            raise _make_backup_format_error("El JSON contiene una clave repetida.")
        fields[field_name] = value

    return fields


def _reject_non_json_number(_value: str) -> None:
    raise _make_backup_format_error("El JSON contiene un número inválido.", code="invalid_syntax")


def _check_unique_ids(
    records: Iterable[BackupRecord],
    collection_name: str,
    ids: set[int],
) -> None:
    for record in records:
        record_id = record.id
        if record_id in ids:
            raise _make_backup_format_error(
                f"El identificador {record_id} está repetido en {collection_name}.",
                location=collection_name,
            )
        ids.add(record_id)


def to_csv(backup: ClientBackup) -> bytes:
    """Genera un CSV con una fila por cliente, etiqueta, proyecto o recurso."""

    # Preparamos el CSV en memoria y escribimos la primera línea con las columnas.
    csv_buffer = StringIO(newline="")
    csv_writer = csv.DictWriter(
        csv_buffer, #Guarda el texto
        fieldnames=_CSV_HEADER, #Indica las columnas
        quoting=csv.QUOTE_ALL, #Pone comillas dobles en todos los campos
    )
    csv_writer.writeheader()

    client = backup.client
    client_id = client.id
    tags = backup.tags
    projects = backup.projects

    # La fila del cliente indica cuántas etiquetas y proyectos contiene la copia.
    client_collection_counts = {
        "tags": len(tags),
        "projects": len(projects),
    }

    # Se copia la fila del cliente.
    _write_csv_row(
        csv_writer,
        "client",
        client,
        collection_counts=client_collection_counts,
    )
    #Bucle para copiar las filas de cada registro de tags
    for tag in tags:
        _write_csv_row(
            csv_writer,
            "tag",
            tag,
            parent_id=client_id,
        )

    for project in projects:
        project_id = project.id

        # Contamos los recursos antes de escribir la fila del proyecto.
        project_collection_counts: dict[str, int] = {}

        for collection_name in PROJECT_RESOURCE_COLLECTIONS.values():
            # Por ejemplo, si collection_name es "notes", esto obtiene project.notes.
            resources = getattr(project, collection_name)
            number_of_resources = len(resources)
            project_collection_counts[collection_name] = number_of_resources

        _write_csv_row(
            csv_writer,
            "project",
            project,
            parent_id=client_id,
            collection_counts=project_collection_counts,
        )

        # Escribimos una fila por recurso y la vinculamos a este proyecto.
        for resource_type, collection_name in PROJECT_RESOURCE_COLLECTIONS.items():
            resources = getattr(project, collection_name)

            for resource in resources:
                _write_csv_row(
                    csv_writer,
                    resource_type,
                    resource,
                    parent_id=project_id,
                )

    # El CSV se ha construido como texto. Lo convertimos a bytes para devolverlo.
    csv_text = csv_buffer.getvalue()
    csv_bytes = csv_text.encode("utf-8")
    return csv_bytes

def _write_csv_row(
    writer: csv.DictWriter,
    entity: str,
    record: BackupRecord,
    parent_id: int | None = None,
    collection_counts: dict[str, int] | None = None,
) -> None:
    #La clave es la columna y el valor la fila
    row: dict[str, str | int] = {
        "schema_version": CSV_BACKUP_SCHEMA_VERSION,
        "entity": entity,
        "id": record.id,
        "parent_id": "",
        "collection_counts": "",
    }
    if parent_id is not None:
        row["parent_id"] = parent_id

    if collection_counts is not None:
        row["collection_counts"] = json.dumps(collection_counts)

    #Define los campos de esa entidad
    field_names = _CSV_FIELDS_BY_ENTITY[entity]

    #Se convierte a set para pasarlo en el 'include'
    #Forma recomendada
    field_names_set_type = set(field_names)

    #Crea un dict que sea compatible con json con el nombre de los campos
    record_fields = record.model_dump(mode="json", include=field_names_set_type)

    for field_name, value in record_fields.items():
        row[field_name] = _convert_value_to_csv_text(value)

    writer.writerow(row)


def _convert_value_to_csv_text(value: str | int | bool | None) -> str:
    if value is None:
        return _CSV_NULL_MARKER

    #Comprueba si value es bool
    if isinstance(value, bool):
        if value is True:
            return "true"
        return "false"
    #Comprueba si value no es string
    if not isinstance(value, str):
        return str(value)

    if value == "":
        return ""

    first_character = value[0]
    # Cc y Cf son las categorías Unicode de control y de formato.
    needs_prefix = (
            first_character in _CSV_START_CHARS_THAT_NEED_PREFIX
            or first_character.isspace()
            #Identifica caracteres invisibles
            or category(first_character) in {"Cc", "Cf"}
    )
    if needs_prefix:
        return _CSV_TEXT_PREFIX + value

    return value


def from_csv(content: bytes) -> ClientBackup:
    """Lee las filas del CSV y las enlaza para reconstruir la copia."""
    try:
        csv_text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise _make_backup_format_error("El CSV debe usar UTF-8.", code="invalid_syntax") from error

    input_buffer = StringIO(csv_text, newline="")
    reader = csv.DictReader(input_buffer, strict=True)

    try:
        if reader.fieldnames != list(_CSV_HEADER):
            raise _make_backup_format_error(
                "La cabecera debe corresponder a un CSV v1 con id, parent_id y recuentos de colecciones.",
                location="cabecera",
            )

        records_by_entity_and_id = _get_csv_records_by_entity_and_id(reader)
    except csv.Error as error:
        raise _make_backup_format_error(
            "El CSV tiene sintaxis inválida.",
            code="invalid_syntax",
            location=f"línea {reader.reader.line_num}",
        ) from error

    return _create_client_backup_from_csv_records(records_by_entity_and_id)


def _get_csv_records_by_entity_and_id(reader: csv.DictReader) -> dict[tuple[str, int], _CsvRecord]:
    # El padre puede aparecer después del hijo. Primero se guardan todas las filas.
    records_by_entity_and_id = {}
    for row in reader:
        #line_number toma el valor de la ultima linea de la fila, aunque ocupe más de 1
        line_number = reader.line_num
        record = _get_csv_record(row, line_number)

        record_id = record.fields["id"]
        record_key = (record.entity, record_id)
        if record_key in records_by_entity_and_id:
            raise _make_backup_format_error(
                f"El id {record_id} está repetido para la entidad {record.entity}.",
                location=f"línea {line_number}, columna id",
            )

        records_by_entity_and_id[record_key] = record

    return records_by_entity_and_id


def _get_csv_record(row: dict[str, str], line_number: int) -> _CsvRecord:
    row_location = f"línea {line_number}"
    if None in row or None in row.values():
        raise _make_backup_format_error("Número de columnas incorrecto.", location=row_location)

    expected_version = str(CSV_BACKUP_SCHEMA_VERSION)
    if row["schema_version"] != expected_version:
        raise _make_backup_format_error("Versión de copia CSV incompatible.", location=row_location)

    entity = row["entity"]
    field_names = _CSV_FIELDS_BY_ENTITY.get(entity)
    if field_names is None:
        raise _make_backup_format_error("Entidad desconocida en el CSV.", location=row_location)

    for column_name in _CSV_DATA_COLUMNS:
        if column_name not in field_names and row[column_name]:
            raise _make_backup_format_error(
                f"La fila de {entity} tiene datos en columnas que no usa.",
                location=row_location,
            )

    record_id = _convert_csv_id_to_int(row["id"], "id", row_location)
    field_values: dict[str, Any] = {"id": record_id}
    for field_name in field_names:
        cell_text = row[field_name]
        try:
            field_values[field_name] = _convert_csv_cell_text_to_value(field_name, cell_text)
        except ValueError as error:
            raise _make_backup_format_error(
                str(error),
                location=f"{row_location}, columna {field_name}",
            ) from error

    parent_id = None
    parent_id_text = row["parent_id"]
    if parent_id_text != "":
        parent_id = _convert_csv_id_to_int(parent_id_text, "parent_id", row_location)

    collection_counts_text = row["collection_counts"]
    if collection_counts_text and entity not in {"client", "project"}:
        raise _make_backup_format_error(
            "Esta entidad no tiene colecciones.",
            location=f"{row_location}, columna collection_counts",
        )

    return _CsvRecord(
        entity=entity,
        parent_id=parent_id,
        fields=field_values,
        line_number=line_number,
        collection_counts_text=collection_counts_text,
    )


def _convert_csv_id_to_int(cell_text: str, column_name: str, row_location: str) -> int:
    location = f"{row_location}, columna {column_name}"
    try:
        id_number = int(cell_text)
    except ValueError as error:
        raise _make_backup_format_error("El id debe ser un entero.", location=location) from error

    if str(id_number) != cell_text:
        raise _make_backup_format_error("El id debe estar escrito como un entero decimal.", location=location)

    return id_number


def _convert_csv_cell_text_to_value(field_name: str, cell_text: str) -> str | bool | None:
    if cell_text == _CSV_NULL_MARKER:
        return None

    if field_name == "is_active":
        if cell_text == "true":
            return True
        if cell_text == "false":
            return False
        raise ValueError("is_active debe ser true o false.")

    if not cell_text.startswith(_CSV_TEXT_PREFIX):
        return cell_text

    #Se vuelve a formatear el texto con las reglas previstas
    #Para evitar manipulaciones manuales en los datos
    format_text = cell_text.removeprefix(_CSV_TEXT_PREFIX)
    if _convert_value_to_csv_text(format_text) != cell_text:
        raise ValueError("Escape de texto inválido.")

    return format_text


def _create_client_backup_from_csv_records(
    records_by_entity_and_id: dict[tuple[str, int], _CsvRecord],
) -> ClientBackup:
    client_records: list[_CsvRecord] = []
    for record in records_by_entity_and_id.values():
        if record.entity == "client":
            client_records.append(record)

    client_error_message = "La copia debe contener un único cliente."
    if len(client_records) != 1:
        raise _make_backup_format_error(client_error_message)

    client_record = client_records[0]
    if client_record.parent_id is not None:
        raise _make_backup_format_error(
            client_error_message,
            location=f"línea {client_record.line_number}, columna parent_id",
        )

    children_by_parent = _organize_children_by_parent(records_by_entity_and_id)
    client_id = client_record.fields["id"]
    tag_records = children_by_parent.get((client_id, "tag"), [])
    project_records = children_by_parent.get((client_id, "project"), [])
    client_collection_counts = {
        "tags": len(tag_records),
        "projects": len(project_records),
    }
    _validate_collection_counts(client_record, client_collection_counts)

    tags_data = []
    for tag_record in tag_records:
        tags_data.append(tag_record.fields)

    projects_data = []
    for project_record in project_records:
        project_data = _create_project_with_child_resources(project_record, children_by_parent)
        projects_data.append(project_data)

    backup_data = {
        "schema_version": JSON_BACKUP_SCHEMA_VERSION,
        "client": client_record.fields,
        "tags": tags_data,
        "projects": projects_data,
    }
    return _validate_backup_model(backup_data)


def _organize_children_by_parent(
    records_by_entity_and_id: dict[tuple[str, int], _CsvRecord],
) -> dict[tuple[int, str], list[_CsvRecord]]:
    children_by_parent: dict[tuple[int, str], list[_CsvRecord]] = defaultdict(list)
    for record in records_by_entity_and_id.values():
        if record.entity == "client":
            continue

        parent_entity = "project"
        if record.entity in {"tag", "project"}:
            parent_entity = "client"

        parent_id = record.parent_id
        if parent_id is None or (parent_entity, parent_id) not in records_by_entity_and_id:
            raise _make_backup_format_error(
                f"parent_id debe apuntar a un registro de tipo {parent_entity} presente en la copia.",
                location=f"línea {record.line_number}, columna parent_id",
            )


        key = (parent_id, record.entity)
        #Si no existe una lista, la crea de manera automática
        children_by_parent[key].append(record)

    return children_by_parent


def _create_project_with_child_resources(
    project_record: _CsvRecord,
    children_by_parent: dict[tuple[int, str], list[_CsvRecord]],
) -> dict[str, Any]:
    project_data = project_record.fields.copy()
    project_id = project_data["id"]

    collection_counts: dict[str, int] = {}
    for entity, collection_name in PROJECT_RESOURCE_COLLECTIONS.items():
        key = (project_id, entity)
        resource_records = children_by_parent.get(key, [])
        collection_data = []
        for resource_record in resource_records:
            collection_data.append(resource_record.fields)

        project_data[collection_name] = collection_data
        collection_counts[collection_name] = len(resource_records)

    _validate_collection_counts(project_record, collection_counts)
    return project_data


def _validate_collection_counts(record: _CsvRecord, row_counts: dict[str, int]) -> None:
    location = f"línea {record.line_number}, columna collection_counts"
    try:
        declared_counts = json.loads(
            record.collection_counts_text,
            object_pairs_hook=_read_json_object,
        )
    except (ValueError, RecursionError) as error:
        raise _make_backup_format_error("Faltan recuentos de colecciones válidos.", location=location) from error

    # Cada colección debe aparecer en el diccionario, incluso si su recuento es 0.
    if isinstance(declared_counts, dict):
        counts_are_integers = True

        for count in declared_counts.values():
            # Comprobamos el tipo exacto para rechazar True y False.
            if type(count) is not int:
                counts_are_integers = False
                break

        # Solo comparamos los recuentos si todos son enteros.
        if counts_are_integers:
            if declared_counts == row_counts:
                return

    raise _make_backup_format_error("Los recuentos no coinciden con las filas del archivo.", location=location)
