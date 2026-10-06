from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.client import Client
from app.models.project import Project
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectRead
from app.security.dependencies import require_project_access, require_client_access, get_active_current_user, \
    require_modifier_role, check_client_access
from app.security.models.user_model import RoleType, User
from app.services import project_service

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]

CurrentProject = Annotated[
    Project, Depends(require_project_access)
]

CurrentClient = Annotated[
    Client, Depends(require_client_access)
]

CurrentUser = Annotated[
    User,
    Depends(get_active_current_user),
]

CurrentWriter = Annotated[
    User, Depends(require_modifier_role)
]


@router.get(
    "",
    response_model=list[ProjectRead]
)
def find_all(
        db: DbSession,
        current_user: CurrentUser,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100)
):
    if current_user.role == RoleType.ADMIN:
        return project_service.get_projects(db, offset, limit)

    return project_service.get_projects_by_users(db, current_user.id, offset, limit)


@router.get(
    "/{project_id}",
    response_model=ProjectRead
)
def find_by_id(
        project: CurrentProject
):
    return project


@router.get(
    "/client/{client_id}",
    response_model=list[ProjectRead]
)
def find_by_client_id(
        db: DbSession,
        client: CurrentClient,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100)
):
    return project_service.get_projects_by_id_client(db, client.id, offset, limit)


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: ProjectCreate,
        current_user: CurrentWriter,

):
    check_client_access(db, current_user, data.client_id)

    return project_service.create_project(db, data)


@router.patch(
    "/{project_id}",
    response_model=ProjectRead
)
def update(
        db: DbSession,
        data: ProjectUpdate,
        current_user: CurrentWriter,
        current_project: CurrentProject,
):
    if data.client_id is not None:
        check_client_access(db, current_user, data.client_id)

    return project_service.update_project(db, current_project.id, data)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        _: CurrentWriter,
        current_project: CurrentProject
) -> None:
    project_service.delete_project(db, current_project.id)


@router.patch(
    "/{project_id}/archive",
    response_model=ProjectRead
)
def archive(
        db: DbSession,
        _: CurrentWriter,
        current_project: CurrentProject
):
    return project_service.archive_project(db, current_project.id)


@router.patch(
    "/{project_id}/restore",
    response_model=ProjectRead
)
def restore(
        db: DbSession,
        _: CurrentWriter,
        current_project: CurrentProject
):
    return project_service.restore_project(db, current_project.id)
