from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.command import Command
from app.models.domain import Domain
from app.models.environment import Environment
from app.models.link import Link
from app.models.note import Note
from app.models.project import Project
from app.models.repository import Repository
from app.models.service import Service
from app.models.user_favorite_project_model import UserFavoriteProject
from app.repositories import project_repo
from app.schemas.project_schema import (
    PaginatedProjectTableRead,
    ProjectCreate,
    ProjectFullCreate,
    ProjectLightRead,
    ProjectUpdate,
)
from app.security.models.log_model import ActionType, EntityType
from app.security.models.user_client_model import UserClient
from app.security.models.user_model import User
from app.security.services import log_service
from app.services import client_service


def _register_project_log(
        db: Session,
        user_id: int,
        action: ActionType,
        project_id: int,
) -> None:
    log_service.register_log(
        db=db,
        user_id=user_id,
        action=action,
        affected_entity=EntityType.PROJECT,
        affected_entity_id=project_id,
    )



def _save_project_with_log(
        db: Session,
        project: Project,
        user_id: int,
        action: ActionType,
) -> Project:
    try:
        project_repo.save(db, project)
        _register_project_log(db, user_id, action, project.id)
        db.commit()
        db.refresh(project)
        return project
    except Exception:
        db.rollback()
        raise

def _commit_and_refresh_project(
        db: Session,
        project: Project,
) -> Project:
    try:
        db.commit()
        db.refresh(project)
        return project
    except Exception:
        db.rollback()
        raise


def _set_project_active_status(
        db: Session,
        project_id: int,
        current_user: User,
        is_active: bool,
) -> Project:
    project = get_project(db, project_id, current_user.id)
    project.is_active = is_active
    return _save_project_with_log(
        db,
        project,
        current_user.id,
        ActionType.UPDATE,
    )


def _find_or_create_client(
        db: Session,
        data: ProjectFullCreate,
        current_user: User,
) -> int | None:
    if data.client_id is not None:
        return client_service.get_active_client(db, data.client_id).id

    if data.client is None:
        return None

    client = Client(
        name=data.client.name,
        cif=data.client.cif,
        phone=data.client.phone,
    )
    db.add(client)
    db.flush()
    db.add(UserClient(user_id=current_user.id, client_id=client.id))

    log_service.register_log(
        db=db,
        user_id=current_user.id,
        action=ActionType.CREATE,
        affected_entity=EntityType.CLIENT,
        affected_entity_id=client.id,
    )
    return client.id


def _add_project_children(
        db: Session,
        project_id: int,
        data: ProjectFullCreate,
) -> None:
    for item in data.environments:
        db.add(Environment(
            project_id=project_id,
            type=item.type,
            url=item.url,
        ))

    for item in data.repositories:
        db.add(Repository(
            project_id=project_id,
            type=item.type,
            url=item.url,
        ))

    for item in data.services:
        db.add(Service(
            project_id=project_id,
            name=item.name,
        ))

    for item in data.domains:
        db.add(Domain(
            project_id=project_id,
            url=item.url,
        ))

    for item in data.commands:
        db.add(Command(
            project_id=project_id,
            name=item.name,
            instruction=item.instruction,
        ))

    for item in data.links:
        db.add(Link(
            project_id=project_id,
            title=item.title,
            url=item.url,
        ))

    for item in data.notes:
        db.add(Note(
            project_id=project_id,
            description=item.description,
            content=item.content,
        ))


def get_project(
        db: Session,
        project_id: int,
        favorite_user_id: int | None = None,
) -> Project:
    project = project_repo.find_by_id(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    if favorite_user_id is not None:
        project_repo.set_favorite_status(db, project, favorite_user_id)
    return project


def get_projects_by_id_client(
        db: Session,
        client_id: int,
        offset: int,
        limit: int,
        favorite_user_id: int,
) -> PaginatedProjectTableRead:
    return project_repo.find_by_client_id(
        db, client_id, offset, limit, favorite_user_id
    )


def get_projects(
        db: Session,
        offset: int,
        limit: int,
        search: str | None = None,
        favorite_user_id: int | None = None,
) -> PaginatedProjectTableRead:
    return project_repo.find_all(
        db, offset, limit, search, favorite_user_id=favorite_user_id
    )


def get_projects_by_users(
        db: Session,
        user_id: int,
        offset: int,
        limit: int,
        search: str | None = None,
) -> PaginatedProjectTableRead:
    return project_repo.find_all_by_users(db, user_id, offset, limit, search)


def get_projects_light(
        db: Session,
        user_id: int,
) -> list[ProjectLightRead]:
    return project_repo.find_all_light(db, user_id)


def get_projects_light_by_users(
        db: Session,
        user_id: int,
) -> list[ProjectLightRead]:
    return project_repo.find_all_light_by_users(db, user_id)


def favorite_project(
        db: Session,
        project_id: int,
        current_user: User,
) -> Project:
    project = get_project(db, project_id, current_user.id)
    favorite = db.get(UserFavoriteProject, (current_user.id, project.id))

    if favorite is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El proyecto ya está en favoritos",
        )

    db.add(
        UserFavoriteProject(user_id=current_user.id, project_id=project.id)
    )
    project.is_favorite = True
    return _commit_and_refresh_project(db, project)


def unfavorite_project(
        db: Session,
        project_id: int,
        current_user: User,
) -> Project:
    project = get_project(db, project_id, current_user.id)
    favorite = db.get(UserFavoriteProject, (current_user.id, project.id))

    if favorite is not None:
        db.delete(favorite)

    project.is_favorite = False
    return _commit_and_refresh_project(db, project)


def get_archived_projects(
        db: Session,
        offset: int,
        limit: int,
        search: str | None = None,
    favorite_user_id: int | None = None,
) -> PaginatedProjectTableRead:
    return project_repo.find_all_archived(
        db, offset, limit, search, favorite_user_id=favorite_user_id
    )


def get_archived_projects_by_users(
        db: Session,
        user_id: int,
        offset: int,
        limit: int,
        search: str | None = None,
) -> PaginatedProjectTableRead:
    return project_repo.find_all_archived_by_users(
        db, user_id, offset, limit, search
    )


def create_project(
        db: Session,
        data: ProjectCreate,
        current_user: User,
) -> Project:
    if data.client_id is not None:
        client_service.get_active_client(db, data.client_id)

    project = Project(
        name=data.name,
        description=data.description,
        client_id=data.client_id,
    )

    return _save_project_with_log(
        db,
        project,
        current_user.id,
        ActionType.CREATE,
    )


def update_project(
        db: Session,
        project_id: int,
        data: ProjectUpdate,
        current_user: User,
) -> Project:
    project = get_project(db, project_id, current_user.id)
    updates = data.model_dump(exclude_unset=True)

    if updates.get("client_id") is not None:
        client_service.get_active_client(db, updates["client_id"])

    for field, value in updates.items():
        setattr(project, field, value)

    return _save_project_with_log(
        db,
        project,
        current_user.id,
        ActionType.UPDATE,
    )


def delete_project(
        db: Session,
        project_id: int,
        current_user: User,
) -> str:
    project = get_project(db, project_id, current_user.id)

    has_dependencies = any((
        project.environments,
        project.repositories,
        project.domains,
        project.links,
        project.services,
        project.commands,
        project.notes,
    ))

    if has_dependencies:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El proyecto aún contiene dependencias activas. "
                "Borra las depencencias primero."
                "Puedes archivar el proyecto en su lugar."
            ),
        )

    project_name = project.name
    client_name = project.client.name if project.client is not None else None

    try:
        project_repo.delete(db, project)

        _register_project_log(
            db,
            current_user.id,
            ActionType.DELETE,
            project.id,
        )
        db.commit()

        if client_name is None:
            return (
                f"El proyecto huérfano {project_name} "
                "ha sido borrado correctamente"
            )
        return (
            f"El proyecto {project_name} del cliente {client_name} "
            "ha sido borrado correctamente"
        )
    except Exception:
        db.rollback()
        raise


def restore_project(
        db: Session,
        project_id: int,
        current_user: User,
) -> Project:
    return _set_project_active_status(
        db,
        project_id,
        current_user,
        is_active=True,
    )


def archive_project(
        db: Session,
        project_id: int,
        current_user: User,
) -> Project:
    return _set_project_active_status(
        db,
        project_id,
        current_user,
        is_active=False,
    )


def get_active_project(
        db: Session,
        project_id: int,
) -> Project:
    project = get_project(db, project_id)

    if not project.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El proyecto está archivado",
        )
    return project


def create_full_project(
        db: Session,
        data: ProjectFullCreate,
        current_user: User,
) -> Project:
    try:
        client_id = _find_or_create_client(db, data, current_user)

        project = Project(
            name=data.name,
            description=data.description,
            is_active=data.is_active,
            client_id=client_id,
        )

        db.add(project)
        db.flush()

        _add_project_children(db, project.id, data)
        _register_project_log(
            db,
            current_user.id,
            ActionType.CREATE,
            project.id,
        )

        return _commit_and_refresh_project(db, project)
    except Exception:
        db.rollback()
        raise
