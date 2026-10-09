from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.command import Command
from app.models.link import Link
from app.models.note import Note
from app.models.project import Project
from app.schemas.project_schema import PaginatedProjectTableRead, ProjectTableRead
from app.security.models.user_client_model import UserClient


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> PaginatedProjectTableRead:
    commands_count_query = (
        select(func.count(Command.id))
        .where(Command.project_id == Project.id)
        .scalar_subquery()
        .label("commands_count")
    )
    links_count_query = (
        select(func.count(Link.id))
        .where(Link.project_id == Project.id)
        .scalar_subquery()
        .label("links_count")
    )
    notes_count_query = (
        select(func.count(Note.id))
        .where(Note.project_id == Project.id)
        .scalar_subquery()
        .label("notes_count")
    )

    total_statement = (
        select(func.count(Project.id))
        .where(Project.is_active.is_(True))
    )
    total = db.scalar(total_statement) or 0

    statement = (
        select(
            Project,
            commands_count_query,
            links_count_query,
            notes_count_query,
        )
        .options(
            # El cliente se carga junto con el proyecto.
            joinedload(Project.client),
            # Cada relación se consulta para todos los proyectos de la página,
            # no una vez por cada proyecto.
            selectinload(Project.environments),
            selectinload(Project.repositories),
            selectinload(Project.services),
            selectinload(Project.domains),
        )
        .where(Project.is_active.is_(True))
        .offset(offset)
        .limit(limit)
        .order_by(Project.id)
    )

    rows = db.execute(statement).all()
    projects: list[ProjectTableRead] = []

    for project, commands_count, links_count, notes_count in rows:
        project_table = ProjectTableRead(
            id=project.id,
            name=project.name,
            client=project.client,
            environments=project.environments,
            repositories=project.repositories,
            services=project.services,
            domains=project.domains,
            commands_count=commands_count,
            links_count=links_count,
            notes_count=notes_count,
        )

        projects.append(project_table)

    return PaginatedProjectTableRead(
        items=projects,
        total=total,
        offset=offset,
        limit=limit,
    )


def find_all_by_users(
        db: Session,
        user_id: int,
        offset: int = 0,
        limit: int = 20,

) -> PaginatedProjectTableRead:
    commands_count_query = (
        select(func.count(Command.id))
        .where(Command.project_id == Project.id)
        .scalar_subquery()
        .label("commands_count")
    )
    links_count_query = (
        select(func.count(Link.id))
        .where(Link.project_id == Project.id)
        .scalar_subquery()
        .label("links_count")
    )
    notes_count_query = (
        select(func.count(Note.id))
        .where(Note.project_id == Project.id)
        .scalar_subquery()
        .label("notes_count")
    )

    total_statement = (
        select(func.count(Project.id))
        .join(UserClient, UserClient.client_id == Project.client_id)
        .where(UserClient.user_id == user_id, Project.is_active.is_(True))
    )
    total = db.scalar(total_statement) or 0

    statement = (
        select(
            Project,
            commands_count_query,
            links_count_query,
            notes_count_query,
        )
        .options(
            joinedload(Project.client),
            selectinload(Project.environments),
            selectinload(Project.repositories),
            selectinload(Project.services),
            selectinload(Project.domains),
        )
        .join(UserClient, UserClient.client_id == Project.client_id)
        .where(UserClient.user_id == user_id, Project.is_active.is_(True))
        .offset(offset)
        .limit(limit)
        .order_by(Project.id)
    )

    rows = db.execute(statement).all()
    projects: list[ProjectTableRead] = []

    for project, commands_count, links_count, notes_count in rows:
        project_table = ProjectTableRead(
            id=project.id,
            name=project.name,
            client=project.client,
            environments=project.environments,
            repositories=project.repositories,
            services=project.services,
            domains=project.domains,
            commands_count=commands_count,
            links_count=links_count,
            notes_count=notes_count,
        )

        projects.append(project_table)

    return PaginatedProjectTableRead(
        items=projects,
        total=total,
        offset=offset,
        limit=limit,
    )


def find_all_archived(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Project]:
    statement = (
        select(Project)
        .where(Project.is_active.is_(False))
        .offset(offset)
        .limit(limit)
        .order_by(Project.id)
    )
    return list(
        db.scalars(statement).all()
    )


def find_by_id(
        db: Session,
        project_id: int,
) -> Project | None:
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


def find_by_client_id(
        db: Session,
        client_id: int,
        offset: int = 0,
        limit: int = 20
) -> PaginatedProjectTableRead:
    commands_count_query = (
        select(func.count(Command.id))
        .where(Command.project_id == Project.id)
        .scalar_subquery()
        .label("commands_count")
    )
    links_count_query = (
        select(func.count(Link.id))
        .where(Link.project_id == Project.id)
        .scalar_subquery()
        .label("links_count")
    )
    notes_count_query = (
        select(func.count(Note.id))
        .where(Note.project_id == Project.id)
        .scalar_subquery()
        .label("notes_count")
    )

    total_statement = (
        select(func.count(Project.id))
        .where(Project.client_id == client_id, Project.is_active.is_(True))
    )
    total = db.scalar(total_statement) or 0

    statement = (
        select(
            Project,
            commands_count_query,
            links_count_query,
            notes_count_query,
        )
        .options(
            joinedload(Project.client),
            selectinload(Project.environments),
            selectinload(Project.repositories),
            selectinload(Project.services),
            selectinload(Project.domains),
        )
        .where(Project.client_id == client_id, Project.is_active.is_(True))
        .offset(offset)
        .limit(limit)
        .order_by(Project.id)
    )

    rows = db.execute(statement).all()
    projects: list[ProjectTableRead] = []

    for project, commands_count, links_count, notes_count in rows:
        project_table = ProjectTableRead(
            id=project.id,
            name=project.name,
            client=project.client,
            environments=project.environments,
            repositories=project.repositories,
            services=project.services,
            domains=project.domains,
            commands_count=commands_count,
            links_count=links_count,
            notes_count=notes_count,
        )
        projects.append(project_table)

    return PaginatedProjectTableRead(
        items=projects,
        total=total,
        offset=offset,
        limit=limit,
    )


def save(
        db: Session,
        project: Project,

) -> Project:
    db.add(project)
    db.flush()
    return project


def delete(
        db: Session,
        project: Project,
) -> None:
    db.delete(project)
