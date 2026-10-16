from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.environment import Environment
from app.models.repository import Repository
from app.models.service import Service
from app.models.domain import Domain
from app.models.command import Command
from app.models.link import Link
from app.models.note import Note
from app.models.project import Project
from app.repositories import project_repo
from app.schemas.project_schema import PaginatedProjectTableRead, ProjectCreate, ProjectUpdate, ProjectFullCreate
from app.security.models.log_model import ActionType, EntityType
from app.security.models.user_client_model import UserClient
from app.security.models.user_model import User
from app.security.services import log_service
from app.services import client_service


def get_project(
        db: Session,
        project_id: int
) -> Project:
    project = project_repo.find_by_id(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    return project


def get_projects_by_id_client(
        db: Session,
        client_id: int,
        offset: int,
        limit: int

) -> PaginatedProjectTableRead:
    projects = project_repo.find_by_client_id(db, client_id, offset, limit)
    return projects


def get_projects(
        db: Session,
        offset: int,
        limit: int
) -> PaginatedProjectTableRead:
    return project_repo.find_all(db, offset, limit)


def get_projects_by_users(
        db: Session,
        user_id: int,
        offset: int,
        limit: int
) -> PaginatedProjectTableRead:
    return project_repo.find_all_by_users(db, user_id, offset, limit)


def get_archived_projects(
        db: Session,
        offset: int,
        limit: int
) -> list[Project]:
    return project_repo.find_all_archived(db, offset, limit)


def create_project(
        db: Session,
        data: ProjectCreate,
        current_user: User
) -> Project:
    client = client_service.get_active_client(db, data.client_id)

    project = Project(
        name=data.name,
        description=data.description,
        client_id=client.id
    )

    try:
        project_repo.save(db, project)

        log_service.register_log(
            db=db,
            user_id=current_user.id,
            action=ActionType.CREATE,
            affected_entity=EntityType.PROJECT,
            affected_entity_id=project.id
        )
        db.commit()
        db.refresh(project)
        return project
    except Exception:
        db.rollback()
        raise


def update_project(
        db: Session,
        project_id: int,
        data: ProjectUpdate,
        current_user: User
) -> Project:
    project = get_project(db, project_id)

    updates = data.model_dump(
        exclude_unset=True
    )
    if "client_id" in updates:
        client_service.get_active_client(db, updates["client_id"])

    for field, value in updates.items():
        setattr(project, field, value)

    try:
        project_repo.save(db, project)

        log_service.register_log(
            db=db,
            user_id=current_user.id,
            action=ActionType.UPDATE,
            affected_entity=EntityType.PROJECT,
            affected_entity_id=project.id
        )
        db.commit()
        db.refresh(project)
        return project
    except Exception:

        db.rollback()
        raise


def delete_project(
        db: Session,
        project_id: int,
        current_user:User
) -> str:
    project = get_project(db, project_id)

    has_dependencies = any((
        project.environments,
        project.repositories,
        project.domains,
        project.links,
        project.services,
        project.commands,
        project.notes
    ))

    if has_dependencies:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El proyecto aún contiene dependencias activas. Borra las depencencias primero."
                "Puedes archivar el proyecto en su lugar."
            ),
        )

    project_name = project.name
    client_name = project.client.name

    try:
        project_repo.delete(db, project)

        log_service.register_log(
            db=db,
            user_id=current_user.id,
            action=ActionType.DELETE,
            affected_entity=EntityType.PROJECT,
            affected_entity_id=project.id
        )
        db.commit()
        return f"El proyecto {project_name} del cliente {client_name} ha sido borrado correctamente"
    except Exception:
        db.rollback()
        raise


def restore_project(
        db: Session,
        project_id: int,
        current_user:User
) -> Project:
    project = get_project(db, project_id)

    project.is_active = True

    try:
        project_repo.save(db, project)

        log_service.register_log(
            db=db,
            user_id=current_user.id,
            action=ActionType.UPDATE,
            affected_entity=EntityType.PROJECT,
            affected_entity_id=project.id
        )
        db.commit()
        db.refresh(project)
        return project
    except Exception:
        db.rollback()
        raise



def archive_project(
        db: Session,
        project_id: int,
        current_user:User
) -> Project:
    project = get_project(db, project_id)

    project.is_active = False

    try:
        project_repo.save(db, project)

        log_service.register_log(
            db=db,
            user_id=current_user.id,
            action=ActionType.UPDATE,
            affected_entity=EntityType.PROJECT,
            affected_entity_id=project.id
        )
        db.commit()
        db.refresh(project)
        return project
    except Exception:
        db.rollback()
        raise


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
        if data.client_id is not None:
            client = client_service.get_active_client(db, data.client_id)
        else:
            client = Client(
                name=data.client.name,
                cif=data.client.cif,
                phone=data.client.phone,
            )
            db.add(client)
            db.flush()

            user_client = UserClient(
                user_id=current_user.id,
                client_id=client.id
            )

            db.add(user_client)

            log_service.register_log(
                db=db,
                user_id=current_user.id,
                action=ActionType.CREATE,
                affected_entity=EntityType.CLIENT,
                affected_entity_id=client.id,
            )

        project = Project(
            name=data.name,
            description=data.description,
            is_active=data.is_active,
            client_id=client.id,
        )

        db.add(project)
        db.flush()


        for item in data.environments:
            environment = Environment(
                project_id=project.id,
                type=item.type,
                url=item.url,
            )
            db.add(environment)

        for item in data.repositories:
            repository = Repository(
                project_id=project.id,
                type=item.type,
                url=item.url,
            )
            db.add(repository)

        for item in data.services:
            service = Service(
                project_id=project.id,
                name=item.name,
            )
            db.add(service)

        for item in data.domains:
            domain = Domain(
                project_id=project.id,
                url=item.url,
            )
            db.add(domain)

        for item in data.commands:
            command = Command(
                project_id=project.id,
                name=item.name,
                instruction=item.instruction,
            )
            db.add(command)

        for item in data.links:
            link = Link(
                project_id=project.id,
                title=item.title,
                url=item.url,
            )
            db.add(link)

        for item in data.notes:
            note = Note(
                project_id=project.id,
                description=item.description,
                content=item.content,
            )
            db.add(note)

        log_service.register_log(
            db=db,
            user_id=current_user.id,
            action=ActionType.CREATE,
            affected_entity=EntityType.PROJECT,
            affected_entity_id=project.id,
        )

        db.commit()
        db.refresh(project)
        return project

    except Exception:
        db.rollback()
        raise
