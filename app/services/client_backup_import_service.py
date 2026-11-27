import json
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database.base import Client, Project, Tag, User
from app.repositories import client_backup_repo
from app.schemas.client_backup_schema import (
    PROJECT_RESOURCE_COLLECTIONS,
    BackupClientDetails,
    BackupFormat,
    BackupImportError,
    BackupImportResult,
    BackupRecord,
    ClientBackup,
    UnassignedBackupProject,
)
from app.security.dependencies import credentials_exception
from app.security.models.log_model import ActionType, EntityType
from app.security.models.user_model import RoleType
from app.security.services import log_service
from app.services import client_backup_format


def _read_backup(content: bytes, backup_format: BackupFormat) -> ClientBackup:
    try:
        if backup_format == "csv":
            return client_backup_format.from_csv(content)
        return client_backup_format.from_json(content)
    except client_backup_format.BackupFormatError as error:
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
        if error.code == "invalid_syntax":
            status_code = status.HTTP_400_BAD_REQUEST

        detail = BackupImportError(code=error.code, message=str(error), location=error.location)
        response_detail = detail.model_dump(exclude_none=True)
        if error.validation_details:
            response_detail.update(error.validation_details)
            # El valor rechazado puede contener texto UTF-8 inválido o números no finitos.
            detail_json = json.dumps(response_detail, ensure_ascii=False, default=str)
            detail_utf8 = detail_json.encode("utf-8", errors="replace")
            response_detail = json.loads(detail_utf8, parse_constant=lambda _constant: None)

        raise HTTPException(
            status_code=status_code,
            detail=response_detail,
        ) from error


def _conflict(
        message: str,
        location: str | None = None,
        projects: list[UnassignedBackupProject] | None = None,
) -> HTTPException:
    detail = BackupImportError(
        code="unassigned_projects" if projects else "conflict",
        message=message,
        location=location,
        projects=projects,
    )
    return HTTPException(status.HTTP_409_CONFLICT, detail=detail.model_dump(exclude_none=True))


def _lock_import_destination(
        database_session: Session,
        user_id: int,
        destination_client_id: int | None,
) -> tuple[User, Client | None]:
    current_user = client_backup_repo.lock_import_user(database_session, user_id)
    if current_user is None:
        raise credentials_exception()
    if not current_user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "La cuenta está desactivada.")

    if destination_client_id is None:
        if current_user.role != RoleType.ADMIN:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Se requieren permisos de administrador.")
        return current_user, None

    if current_user.role not in {RoleType.ADMIN, RoleType.USER}:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Se requieren permisos de escritura.")

    client = client_backup_repo.lock_client_for_restore(database_session, destination_client_id)
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado.")
    if current_user.role == RoleType.ADMIN:
        return current_user, client

    access = client_backup_repo.lock_client_access(database_session, user_id, client.id)
    if access is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes acceso al cliente de destino.")
    return current_user, client


def _check_unique_fields(
        database_session: Session,
        backup: ClientBackup,
        destination_client_id: int | None,
) -> None:
    conflicting_field = client_backup_repo.find_client_conflict(database_session, backup.client, destination_client_id)
    if conflicting_field is not None:
        raise _conflict("Otro cliente ya usa este valor.", location=f"client.{conflicting_field}")

    for field_name in ("mac", "ip"):
        identifier_values = []
        for tag in backup.tags:
            identifier = getattr(tag, field_name)
            if identifier is not None:
                identifier_values.append(identifier)

        if len(identifier_values) != len(set(identifier_values)):
            raise _conflict("Hay dispositivos con el mismo valor en la copia.", location=f"tags.{field_name}")
        if client_backup_repo.tag_identifier_is_used(
                database_session, field_name, identifier_values, destination_client_id
        ):
            raise _conflict("Un dispositivo de otro cliente ya usa este valor.", location=f"tags.{field_name}")


def _check_existing_project_confirmations(
        # Proyectos ya en el sistema
        matching_projects: dict[str, Project],
        unassigned_projects: list[UnassignedBackupProject],
        confirmed_project_ids: frozenset[int],
        current_user: User,
) -> None:
    matching_project_ids = set()
    for project in matching_projects.values():
        matching_project_ids.add(project.id)

    for confirmed_id in confirmed_project_ids:
        if confirmed_id not in matching_project_ids:
            raise _conflict(
                "Los proyectos confirmados cambiaron. Vuelve a comprobar los candidatos.",
                location="projects",
            )
    has_pending_confirmation = False
    for project in unassigned_projects:
        if project.id not in confirmed_project_ids:
            has_pending_confirmation = True
            break

    if not has_pending_confirmation:
        return

    if current_user.role != RoleType.ADMIN:
        raise _conflict(
            "Un administrador debe confirmar los proyectos sin cliente.",
            location="projects",
        )
    raise _conflict(
        "Confirma qué proyectos sin cliente se deben vincular.",
        location="projects",
        projects=unassigned_projects,
    )


def _lock_matching_projects(
        database_session: Session,
        backup: ClientBackup,
        current_user: User,
        destination_client_id: int | None,
        confirmed_project_ids: frozenset[int],
) -> dict[str, Project]:
    project_names = set()

    for backup_project in backup.projects:
        project_name = backup_project.name

        if project_name in project_names:
            raise _conflict(
                "Hay proyectos con el mismo nombre en la copia.",
                location="projects",
            )

        project_names.add(project_name)

    has_confirmations = len(confirmed_project_ids) > 0
    is_admin = current_user.role == RoleType.ADMIN

    if has_confirmations and not is_admin:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Solo un administrador puede confirmar vinculaciones.",
        )

    existing_projects = client_backup_repo.lock_projects_by_name(
        database_session,
        project_names,
    )

    matching_projects: dict[str, Project] = {}
    unassigned_projects: list[UnassignedBackupProject] = []

    for project in existing_projects:
        project_name = project.name

        if project_name not in project_names:
            raise _conflict(
                "Ya existe un proyecto con una variante de ese nombre.",
                location="projects",
            )

        project_has_client: bool = project.client_id is not None

        if project.client_id is not None and not project.client_id == destination_client_id:
            raise _conflict(
                "Un proyecto de la copia pertenece a otro cliente.",
                location="projects",
            )

        if not project_has_client:
            unassigned_project = UnassignedBackupProject(
                id=project.id,
                name=project_name,
            )
            unassigned_projects.append(unassigned_project)

        matching_projects[project_name] = project

    _check_existing_project_confirmations(
        matching_projects,
        unassigned_projects,
        confirmed_project_ids,
        current_user,
    )

    return matching_projects


def _update_fields(record: Client | Project, backup_values: dict) -> bool:
    fields_changed = False
    for field_name, backup_value in backup_values.items():
        if getattr(record, field_name) != backup_value:
            setattr(record, field_name, backup_value)
            fields_changed = True
    return fields_changed


def _record_audit_logs(
        database_session: Session,
        user_id: int,
        action: ActionType,
        entity_type: EntityType,
        records: list,
) -> None:
    for record in records:
        log_service.register_log(database_session, user_id, action, record.id, entity_type)


def _save_client(
        database_session: Session,
        backup_client: BackupClientDetails,
        destination: Client | None,
        user_id: int,
) -> BackupImportResult:
    if destination is None:
        client = Client(
            name=backup_client.name,
            cif=backup_client.cif,
            phone=backup_client.phone,
            is_active=backup_client.is_active,
        )
        database_session.add(client)
        database_session.flush()  # Obtiene el ID antes de registrar la creación del cliente.

        _record_audit_logs(
            database_session,
            user_id,
            ActionType.CREATE,
            EntityType.CLIENT,
            [client],
        )

        return BackupImportResult(client_id=client.id, created=1)

    client_fields = backup_client.model_dump(exclude={"id"})
    fields_changed = _update_fields(destination, client_fields)

    if not fields_changed:
        return BackupImportResult(client_id=destination.id)

    _record_audit_logs(
        database_session,
        user_id,
        ActionType.UPDATE,
        EntityType.CLIENT,
        [destination],
    )

    return BackupImportResult(client_id=destination.id, updated=1)


def _update_existing_project(project: Project, project_fields: dict, result: BackupImportResult) -> bool:
    fields_changed = _update_fields(project, project_fields)
    if fields_changed:
        result.updated += 1

    if project.client_id is not None:
        return fields_changed

    project.client_id = result.client_id
    result.linked += 1
    return True


def _restore_projects(
        database_session: Session,
        backup: ClientBackup,
        matching_projects: dict[str, Project],
        user_id: int,
        result: BackupImportResult,
) -> dict[str, Project]:
    restored_projects: dict[str, Project] = {}
    created_projects: list[Project] = []
    modified_projects: list[Project] = []

    for backup_project in backup.projects:
        project_fields = backup_project.model_dump(
            include={"name", "description", "is_active"},
        )
        project = matching_projects.get(backup_project.name)

        if project is None:
            project = Project(
                client_id=result.client_id,
                name=project_fields["name"],
                description=project_fields["description"],
                is_active=project_fields["is_active"],
            )
            created_projects.append(project)
        else:
            project_was_modified = _update_existing_project(
                project, project_fields, result
            )
            if project_was_modified:
                modified_projects.append(project)

        restored_projects[backup_project.name] = project

    database_session.add_all(created_projects)
    if created_projects or modified_projects:
        database_session.flush()

    _record_audit_logs(
        database_session, user_id, ActionType.CREATE, EntityType.PROJECT, created_projects
    )
    _record_audit_logs(
        database_session, user_id, ActionType.UPDATE, EntityType.PROJECT, modified_projects
    )

    result.created += len(created_projects)
    return restored_projects


def _prepare_records_to_remove_and_create(
        record_model: type,
        parent_field: str,
        parent_id: int,
        current_records: list,
        backup_records: list[BackupRecord],
) -> tuple[list, list]:
    if not backup_records:
        return current_records, []

    first_backup_values = backup_records[0].model_dump(exclude={"id"})
    field_names = list(first_backup_values)

    pending_records_by_values = {}

    for current_record in current_records:
        values = []
        for field_name in field_names:
            values.append(getattr(current_record, field_name))

        key = tuple(values)

        if key not in pending_records_by_values:
            pending_records_by_values[key] = []

        pending_records_by_values[key].append(current_record)

    backup_values_to_create = []

    for backup_record in backup_records:
        backup_values = backup_record.model_dump(exclude={"id"})

        values = []
        for field_name in field_names:
            values.append(backup_values[field_name])

        key = tuple(values)
        pending_matches = pending_records_by_values.get(key)

        if pending_matches:
            pending_matches.pop(0)
        else:
            backup_values_to_create.append(backup_values)

    records_to_remove = []
    for pending_records in pending_records_by_values.values():
        records_to_remove.extend(pending_records)

    # Crea los objetos nuevos y les asigna los atributos uno por uno.
    records_to_create = []
    for backup_values in backup_values_to_create:
        new_record = record_model()

        for field_name, value in backup_values.items():
            setattr(new_record, field_name, value)

        setattr(new_record, parent_field, parent_id)
        records_to_create.append(new_record)

    return records_to_remove, records_to_create


def _delete_and_create_records(
        database_session: Session,
        user_id: int,
        entity_type: EntityType,
        removed_records: list,
        new_records: list,
        result: BackupImportResult,
) -> None:
    _record_audit_logs(database_session, user_id, ActionType.DELETE, entity_type, removed_records)
    for record in removed_records:
        database_session.delete(record)
    if entity_type == EntityType.TAG and removed_records and new_records:
        # Una MAC o IP puede reutilizarse
        database_session.flush()

    if new_records:
        database_session.add_all(new_records)
        database_session.flush()
    _record_audit_logs(database_session, user_id, ActionType.CREATE, entity_type, new_records)
    result.created += len(new_records)
    result.deleted += len(removed_records)


def _restore_project_resources(
        database_session: Session,
        backup: ClientBackup,
        restored_projects: dict[str, Project],
        existing_project_ids: list[int],
        user_id: int,
        result: BackupImportResult,
) -> None:
    for entity, collection in PROJECT_RESOURCE_COLLECTIONS.items():
        resource_model = client_backup_repo.PROJECT_RESOURCE_MODELS[collection]
        existing_by_project = client_backup_repo.lock_project_resource_rows(
            database_session, collection, existing_project_ids
        )
        removed_records = []
        new_records = []
        for backup_project in backup.projects:
            project_id = restored_projects[backup_project.name].id
            removed, added = _prepare_records_to_remove_and_create(
                resource_model,
                "project_id",
                project_id,
                existing_by_project.get(project_id, []),
                getattr(backup_project, collection),
            )
            removed_records.extend(removed)
            new_records.extend(added)
        _delete_and_create_records(
            database_session, user_id, EntityType(entity.upper()), removed_records, new_records, result
        )


def _apply_client_backup(
        database_session: Session,
        backup: ClientBackup,
        destination: Client | None,
        matching_projects: dict[str, Project],
        user_id: int,
) -> BackupImportResult:
    existing_tags = []
    if destination is not None:
        existing_tags = client_backup_repo.lock_tags_for_restore(database_session, destination.id)

    result = _save_client(database_session, backup.client, destination, user_id)
    restored_projects = _restore_projects(database_session, backup, matching_projects, user_id, result)

    removed_tags, new_tags = _prepare_records_to_remove_and_create(Tag, "client_id", result.client_id, existing_tags,
                                                                   backup.tags)
    _delete_and_create_records(database_session, user_id, EntityType.TAG, removed_tags, new_tags, result)

    existing_project_ids = []

    for project in matching_projects.values():
        existing_project_ids.append(project.id)
    _restore_project_resources(database_session, backup, restored_projects, existing_project_ids, user_id, result)
    return result


def import_client_backup(
        database_session: Session,
        user_id: int,
        content: bytes,
        backup_format: BackupFormat,
        destination_client_id: int | None = None,
        confirmed_project_ids: frozenset[int] = frozenset(),
) -> BackupImportResult:
    try:
        backup = _read_backup(content, backup_format)
        current_user, destination = _lock_import_destination(database_session, user_id, destination_client_id)
        _check_unique_fields(database_session, backup, destination_client_id)
        matching_projects = _lock_matching_projects(
            database_session, backup, current_user, destination_client_id, confirmed_project_ids
        )
        result = _apply_client_backup(database_session, backup, destination, matching_projects, user_id)

        database_session.commit()
    except IntegrityError as error:
        database_session.rollback()
        raise _conflict(
        "Los datos de la copia incumplen una restricción de la base de datos. Revisa la copia."
        ) from error
    except Exception:
            database_session.rollback()
            raise

    return result
