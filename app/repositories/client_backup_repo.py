from collections import defaultdict
from operator import attrgetter

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.base import (
    Client,
    Command,
    Domain,
    Environment,
    Link,
    Note,
    Project,
    Repository,
    Service,
    Tag,
    User,
    UserClient,
)
from app.schemas.client_backup_schema import (
    JSON_BACKUP_SCHEMA_VERSION,
    PROJECT_RESOURCE_COLLECTIONS,
    BackupClientDetails,
    ClientBackup,
)


PROJECT_RESOURCE_MODELS = {
    "environments": Environment,
    "repositories": Repository,
    "domains": Domain,
    "links": Link,
    "services": Service,
    "commands": Command,
    "notes": Note,
}

# Abre una transacción de solo lectura para la exportación.
# Todas sus consultas ven los datos tal como estaban en la primera lectura,
# aunque otra sesión los modifique mientras se genera la copia.
def begin_backup_read_transaction(database_session: Session) -> None:
    if database_session.in_transaction():
        raise RuntimeError("No se puede iniciar la transacción de lectura si ya hay una transacción activa.")

    # MySQL reutiliza los datos de la primera lectura en todas las consultas de esta transaccion
    connection = database_session.connection(execution_options={"isolation_level": "REPEATABLE READ"})
    connection.exec_driver_sql("START TRANSACTION READ ONLY")


def find_by_client_id(database_session: Session, client_id: int) -> ClientBackup | None:
    statement = (
        select(Client)
        .where(Client.id == client_id)
        .options(
            selectinload(Client.tags),
            selectinload(Client.projects).options(
                selectinload(Project.environments),
                selectinload(Project.repositories),
                selectinload(Project.domains),
                selectinload(Project.links),
                selectinload(Project.services),
                selectinload(Project.commands),
                selectinload(Project.notes),
            ),
        )
    )
    client = database_session.scalar(statement)
    if client is None:
        return None

    backup = ClientBackup.model_validate(
        {
            "schema_version": JSON_BACKUP_SCHEMA_VERSION,
            "client": client,
            "tags": client.tags,
            "projects": client.projects,
        }
    )
    #Ordena todos los registros por su 'id' de menor a mayor, incluyendo
    #las tablas hijas dependientes del proyecto.
    by_record_id = attrgetter("id")
    backup.tags.sort(key=by_record_id)
    backup.projects.sort(key=by_record_id)
    for project in backup.projects:
        for collection in PROJECT_RESOURCE_COLLECTIONS.values():
            getattr(project, collection).sort(key=by_record_id)
    return backup

#with_for_update => bloquea la modificacion/eliminacion de datos mientras
#dura la transacción. Bloqueo compartido
#populate_existing => refresca el  User por si su valor es diferente en memoria que en la bdd.
def lock_import_user(database_session: Session, user_id: int) -> User | None:
    return database_session.get(User, user_id, with_for_update={"read": True}, populate_existing=True)

#Este bloqueo es exclusivo.
def lock_client_for_restore(database_session: Session, client_id: int) -> Client | None:
    return database_session.get(Client, client_id, with_for_update=True, populate_existing=True)


def lock_client_access(database_session: Session, user_id: int, client_id: int) -> UserClient | None:
    return database_session.get(
        UserClient, (user_id, client_id), with_for_update={"read": True}, populate_existing=True
    )


def find_client_conflict(
    database_session: Session,
    backup_client: BackupClientDetails,
    destination_client_id: int | None,
) -> str | None:
    fields_to_check = [
        (Client.name, backup_client.name),
        (Client.cif, backup_client.cif),
        (Client.phone, backup_client.phone),
    ]

    for client_column, backup_value in fields_to_check:
        if backup_value is None:
            continue

        # Equivale a:
        # SELECT id FROM clients
        # WHERE phone = :backup_value
        #   AND id != :destination_client_id

        query = select(Client.id).where(client_column == backup_value)

        if destination_client_id is not None:
            query = query.where(Client.id != destination_client_id)


        #Si encuentra coincidencias, devuelve la columna afectada
        matching_client_id = database_session.scalar(query)
        if matching_client_id is not None:
            return client_column.key

    return None

#Bloquea de manera exclusiva las filas de los proyectos que coincidan por el nombre
def lock_projects_by_name(database_session: Session, project_names: set[str]) -> list[Project]:
    if not project_names:
        return []
    statement = (
        select(Project)
        .where(Project.name.in_(project_names))
        .order_by(Project.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    return list(database_session.scalars(statement))


def tag_identifier_is_used(
    database_session: Session,
    field_name: str,
    values: list[str],
    destination_client_id: int | None,
) -> bool:
    if not values:
        return False

    if field_name == "mac":
        identifier_column = Tag.mac
    else:
        identifier_column = Tag.ip

    statement = select(Tag.id).where(identifier_column.in_(values))

    if destination_client_id is not None:
        statement = statement.where(Tag.client_id != destination_client_id)

    # Una sola coincidencia basta para detectar el conflicto.
    statement = statement.limit(1)
    found_tag_id = database_session.scalar(statement)

    return found_tag_id is not None


#Bloquea de manera exclusiva las filas de los dispositivos que coincidan con el id del cliente
def lock_tags_for_restore(database_session: Session, client_id: int) -> list[Tag]:
    statement = (
        select(Tag)
        .where(Tag.client_id == client_id)
        .order_by(Tag.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    return list(database_session.scalars(statement))


def lock_project_resource_rows(
    database_session: Session,
    collection: str,
    project_ids: list[int],
) -> dict[int, list]:
    resources_by_project_id: dict[int, list] = defaultdict(list)

    if not project_ids:
        return resources_by_project_id

    resource_model = PROJECT_RESOURCE_MODELS[collection]
    #Equivale a:
    #SELECT *
    #FROM notes
    #WHERE notes.project_id IN (10,30)
    #ORDER BY notes.project_id ASC, notes.id ASC.
    statement = (
        select(resource_model)
        .where(resource_model.project_id.in_(project_ids))
        .order_by(resource_model.project_id, resource_model.id)
    )

    # Bloquea las filas de manera exclusiva y refresca los objetos ya cargados en la sesión.
    statement = statement.with_for_update()
    statement = statement.execution_options(populate_existing=True)

    resources = database_session.scalars(statement)

    for resource in resources:
        project_id = resource.project_id
        resources_by_project_id[project_id].append(resource)

    return resources_by_project_id