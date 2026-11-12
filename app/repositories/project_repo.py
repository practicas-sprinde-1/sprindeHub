from sqlalchemy import exists, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.client import Client
from app.models.command import Command
from app.models.link import Link
from app.models.note import Note
from app.models.project import Project
from app.models.user_favorite_client_model import UserFavoriteClient
from app.models.user_favorite_project_model import UserFavoriteProject
from app.schemas.project_schema import (
    PaginatedProjectTableRead,
    ProjectLightRead,
    ProjectTableRead,
)
from app.security.models.user_client_model import UserClient

#Metodo auxiliar para ver si un proyecto es favorito de un usuario
def _favorite_query(user_id: int):
    return exists().where(
        UserFavoriteProject.user_id == user_id,
        UserFavoriteProject.project_id == Project.id,
    )

#Metodo auxiliar para ver si el cliente del proyecto es favorito del usuario
def _client_favorite_query(user_id: int):
    return exists().where(
        UserFavoriteClient.user_id == user_id,
        UserFavoriteClient.client_id == Project.client_id,
    )

#Metodo que crea 2 columnas, 1 para el proyecto y otra para el cliente
def _favorite_columns(user_id: int | None):
    if user_id is None:
        return False, False

    return (
        #Columna del proyecto
        _favorite_query(user_id).label("is_favorite"),
        #Columna del cliente
        _client_favorite_query(user_id).label("client_is_favorite"),
    )


def _get_items_counts():
    commands_count = (
        select(func.count(Command.id))
        .where(Command.project_id == Project.id)
        # Convierte el select en un valor único para usarlo como columna en la consulta principal
        #(SELECT count(command.id) FROM command WHERE command.project_id = project.id)
        .scalar_subquery()
        .label("commands_count")
    )
    links_count = (
        select(func.count(Link.id))
        .where(Link.project_id == Project.id)
        .scalar_subquery()
        .label("links_count")
    )
    notes_count = (
        select(func.count(Note.id))
        .where(Note.project_id == Project.id)
        .scalar_subquery()
        .label("notes_count")
    )
    return commands_count, links_count, notes_count


def _project_table_load_options():
    return (
        #Carga en memoria mediante un LEFT OUTER JOIN los proyectos y sus clientes
        joinedload(Project.client),
        #Esto equivale a:
        #SELECT environment.id, environment.name, environment.project_id FROM environment
        # WHERE environment.project_id IN (1, 2, 3);
        selectinload(Project.environments),
        selectinload(Project.repositories),
        selectinload(Project.services),
        selectinload(Project.domains),
    )

def _apply_project_search(statement, search: str | None):
    if not search:
        return statement
    search_pattern = f"%{search.strip()}%"
    #outerjoin = Left Outer Join
    return statement.outerjoin(
        Client,
        Client.id == Project.client_id,
    ).where(
        or_(
            Project.name.ilike(search_pattern),
            Client.name.ilike(search_pattern)
        )
    )

def _apply_user_permissions(statement, user_id: int | None):
    if user_id is None:
        return statement

    return statement.join(
        UserClient,
        UserClient.client_id == Project.client_id,
    ).where(UserClient.user_id == user_id)



def _to_project_table_read(row) -> ProjectTableRead:
    #Desempaquetado de la fila
    (
        project,
        commands_count,
        links_count,
        notes_count,
        is_favorite,
        client_is_favorite,
    ) = row

    if project.client is not None:
        project.client.is_favorite = bool(client_is_favorite)

    return ProjectTableRead(
        id=project.id,
        name=project.name,
        is_favorite=bool(is_favorite),
        client=project.client,
        environments=project.environments,
        repositories=project.repositories,
        services=project.services,
        domains=project.domains,
        commands_count=commands_count,
        links_count=links_count,
        notes_count=notes_count,
    )


def _find_all(
    db: Session,
    project_filters:tuple,
    offset: int,
    limit: int,
    search: str | None = None,
    favorite_user_id: int | None = None,
    access_user_id: int | None = None,
) -> PaginatedProjectTableRead:

    # Se utiliza el * para extraer (desempaquetar) los elementos de la lista 'project_filters'.
    # Esto hace que (filtro1, filtro2) se envíe como .where(filtro1, filtro2), combinándolos con un AND.
    total_statement = select(func.count(Project.id)).where(*project_filters)
    total_statement = _apply_user_permissions(total_statement, access_user_id)
    total_statement = _apply_project_search(total_statement, search)
    total = db.scalar(total_statement) or 0

    commands_count, links_count, notes_count = _get_items_counts()
    project_is_favorite, client_is_favorite = _favorite_columns(
        favorite_user_id
    )
    statement = (
        select(
            Project,
            commands_count,
            links_count,
            notes_count,
            project_is_favorite,
            client_is_favorite,
        )
        #.options utiliza los joins que contiene el metodo auxiliar
        .options(*_project_table_load_options())
        .where(*project_filters)
    )
    statement = _apply_user_permissions(statement, access_user_id)
    statement = _apply_project_search(statement, search)
    statement = statement.offset(offset).limit(limit).order_by(Project.id)

    rows = db.execute(statement).all()
    projects =[]

    for row in rows:
        formatted_project = _to_project_table_read(row)
        projects.append(formatted_project)

    return PaginatedProjectTableRead(
        items=projects,
        total=total,
        offset=offset,
        limit=limit,
    )


def find_all(
    db: Session,
    offset: int = 0,
    limit: int = 20,
    search: str | None = None,
    favorite_user_id: int | None = None,
    only_favorites: bool = False,
) -> PaginatedProjectTableRead:
    #project_filter = [OPCION A] if [CONDICION] else [OPCION B]
    project_filter = (
        Project.id.in_(
            select(UserFavoriteProject.project_id).where(
                UserFavoriteProject.user_id == favorite_user_id
            )
        )
        if favorite_user_id is not None and only_favorites
        else Project.is_active.is_(True)
    )
    return _find_all(
        db=db,
        project_filters=(project_filter,),
        offset=offset,
        limit=limit,
        search=search,
        favorite_user_id=favorite_user_id,
    )


def find_all_by_users(
    db: Session,
    user_id: int,
    offset: int = 0,
    limit: int = 20,
    search: str | None = None,
) -> PaginatedProjectTableRead:
    return _find_all(
        db=db,
        project_filters=(Project.is_active.is_(True),),
        offset=offset,
        limit=limit,
        search=search,
        favorite_user_id=user_id,
        access_user_id=user_id,
    )


def find_all_archived(
    db: Session,
    offset: int = 0,
    limit: int = 20,
    search: str | None = None,
    favorite_user_id: int | None = None,
) -> PaginatedProjectTableRead:
    return _find_all(
        db=db,
        project_filters=(Project.is_active.is_(False),),
        offset=offset,
        limit=limit,
        search=search,
        favorite_user_id=favorite_user_id,
    )


def find_all_archived_by_users(
    db: Session,
    user_id: int,
    offset: int = 0,
    limit: int = 20,
    search: str | None = None,
) -> PaginatedProjectTableRead:
    return _find_all(
        db=db,
        project_filters=(Project.is_active.is_(False),),
        offset=offset,
        limit=limit,
        search=search,
        favorite_user_id=user_id,
        access_user_id=user_id,
    )


def find_by_id(db: Session, project_id: int) -> Project | None:
    statement = (
        select(Project)
        .options(
            joinedload(Project.client),
            selectinload(Project.environments),
            selectinload(Project.repositories),
            selectinload(Project.domains),
            selectinload(Project.links),
            selectinload(Project.services),
            selectinload(Project.commands),
            selectinload(Project.notes),
        )
        .where(Project.id == project_id)
    )
    return db.scalar(statement)


def set_favorite_status(
    db: Session,
    project: Project,
    user_id: int,
) -> Project:
    project.is_favorite = bool(
        db.scalar(
            select(
                exists().where(
                    UserFavoriteProject.user_id == user_id,
                    UserFavoriteProject.project_id == project.id,
                )
            )
        )
    )
    if project.client is not None:
        project.client.is_favorite = bool(
            db.scalar(
                select(
                    exists().where(
                        UserFavoriteClient.user_id == user_id,
                        UserFavoriteClient.client_id == project.client.id,
                    )
                )
            )
        )
    return project


def _to_light_projects(rows) -> list[ProjectLightRead]:
    light_projects=[]
    for row in rows:
        project = ProjectLightRead(
            id=row.id,
            name=row.name,
            is_favorite=row.is_favorite,
        )
        light_projects.append(project)
    return light_projects


def find_all_light(db: Session, user_id: int) -> list[ProjectLightRead]:
    statement = (
        select(
            Project.id,
            Project.name,
            _favorite_query(user_id).label("is_favorite"),
        )
        .where(Project.is_active.is_(True))
        .order_by(Project.id)
    )
    rows = db.execute(statement).all()
    return _to_light_projects(rows)


def find_all_light_by_users(
    db: Session,
    user_id: int,
) -> list[ProjectLightRead]:
    statement = (
        select(
            Project.id,
            Project.name,
            _favorite_query(user_id).label("is_favorite"),
        )
        .join(UserClient, UserClient.client_id == Project.client_id)
        .where(
            Project.is_active.is_(True),
            UserClient.user_id == user_id,
        )
        .order_by(Project.id)
    )
    rows = db.execute(statement).all()
    return _to_light_projects(rows)


def find_by_client_id(
    db: Session,
    client_id: int,
    offset: int = 0,
    limit: int = 20,
    favorite_user_id: int | None = None,
) -> PaginatedProjectTableRead:
    return _find_all(
        db=db,
        project_filters=(
            Project.client_id == client_id,
            Project.is_active.is_(True),
        ),
        offset=offset,
        limit=limit,
        favorite_user_id=favorite_user_id,
    )


def save(db: Session, project: Project) -> Project:
    if not hasattr(project, "is_favorite"):
        project.is_favorite = False
    db.add(project)
    db.flush()
    return project


def delete(db: Session, project: Project) -> None:
    db.delete(project)


def find_by_name(
        db: Session,
        name: str,
) -> Project | None:
    statement = select(Project).where(Project.name == name)

    return db.scalar(statement)

