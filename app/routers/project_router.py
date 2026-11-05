from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.client import Client
from app.models.project import Project
from app.schemas.project_schema import (
    PaginatedProjectTableRead,
    ProjectCreate,
    ProjectDetailRead,
    ProjectFullCreate,
    ProjectLightRead,
    ProjectRead,
    ProjectUpdate,
)
from app.schemas.user_favorite_project_schema import UserFavoriteProjectAccess
from app.security.dependencies import (
    check_client_access,
    get_active_current_user,
    require_client_access,
    require_modifier_role,
    require_project_access,
)
from app.security.models.user_model import RoleType, User
from app.services import project_service, user_favorite_project_service

router = APIRouter(prefix="/projects", tags=["projects"])

DbSession = Annotated[Session, Depends(get_db)]
ProjectWithAccess = Annotated[Project, Depends(require_project_access)]
ClientWithAccess = Annotated[Client, Depends(require_client_access)]
CurrentUser = Annotated[User, Depends(get_active_current_user)]
CurrentWriter = Annotated[User, Depends(require_modifier_role)]
PaginationOffset = Annotated[int, Query(ge=0)]
PaginationLimit = Annotated[int, Query(ge=1, le=100)]
ProjectSearch = Annotated[str | None, Query(min_length=1, max_length=120)]


def _get_project_with_client_access(
    db: Session,
    user: User,
    project_id: int,
) -> Project:
    project = project_service.get_project(db, project_id)
    check_client_access(db, user, project.client_id)
    return project


def _validate_optional_client_access(
    db: Session,
    user: User,
    client_id: int | None,
) -> None:
    if client_id is None:
        return

    check_client_access(db, user, client_id)


@router.get("", response_model=PaginatedProjectTableRead)
def list_projects(
    db: DbSession,
    current_user: CurrentUser,
    offset: PaginationOffset = 0,
    limit: PaginationLimit = 20,
    search: ProjectSearch = None,
):
    if current_user.role == RoleType.ADMIN:
        return project_service.get_projects(
            db,
            offset,
            limit,
            search,
            favorite_user_id=current_user.id,
        )

    return project_service.get_projects_by_users(
        db,
        current_user.id,
        offset,
        limit,
        search,
    )


@router.get("/archived", response_model=PaginatedProjectTableRead)
def list_archived_projects(
    db: DbSession,
    current_user: CurrentUser,
    offset: PaginationOffset = 0,
    limit: PaginationLimit = 20,
    search: ProjectSearch = None,
):
    if current_user.role == RoleType.ADMIN:
        return project_service.get_archived_projects(
            db,
            offset,
            limit,
            search,
            favorite_user_id=current_user.id,
        )

    return project_service.get_archived_projects_by_users(
        db,
        current_user.id,
        offset,
        limit,
        search,
    )


@router.get("/light", response_model=list[ProjectLightRead])
def list_light_projects(
    db: DbSession,
    current_user: CurrentUser,
):
    if current_user.role == RoleType.ADMIN:
        return project_service.get_projects_light(db, current_user.id)

    return project_service.get_projects_light_by_users(db, current_user.id)


@router.get("/favorites", response_model=PaginatedProjectTableRead)
def list_favorite_projects(
    db: DbSession,
    current_user: CurrentUser,
    offset: PaginationOffset = 0,
    limit: PaginationLimit = 20,
):
    return user_favorite_project_service.get_user_favorite_projects_by_user_id(
        db,
        current_user.id,
        offset,
        limit,
    )


@router.patch("/{project_id}/favorite", response_model=ProjectRead)
def add_project_to_favorites(
    db: DbSession,
    current_user: CurrentUser,
    access: Annotated[UserFavoriteProjectAccess, Depends()],
):
    project = _get_project_with_client_access(db, current_user, access.project_id)
    return project_service.favorite_project(db, project.id, current_user)


@router.patch("/{project_id}/unfavorite", response_model=ProjectRead)
def remove_project_from_favorites(
    db: DbSession,
    current_user: CurrentUser,
    access: Annotated[UserFavoriteProjectAccess, Depends()],
):
    project = _get_project_with_client_access(db, current_user, access.project_id)
    return project_service.unfavorite_project(db, project.id, current_user)


@router.get("/{project_id}", response_model=ProjectDetailRead)
def get_project(project: ProjectWithAccess):
    return project


@router.get("/client/{client_id}", response_model=PaginatedProjectTableRead)
def list_projects_by_client(
    db: DbSession,
    current_user: CurrentUser,
    client: ClientWithAccess,
    offset: PaginationOffset = 0,
    limit: PaginationLimit = 20,
):
    return project_service.get_projects_by_id_client(
        db,
        client.id,
        offset,
        limit,
        current_user.id,
    )


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    db: DbSession,
    data: ProjectCreate,
    current_user: CurrentWriter,
):
    check_client_access(db, current_user, data.client_id)
    return project_service.create_project(db, data, current_user)


@router.post(
    "/create-completed-project",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_completed_project(
    db: DbSession,
    data: ProjectFullCreate,
    current_user: CurrentWriter,
):
    _validate_optional_client_access(db, current_user, data.client_id)
    return project_service.create_full_project(db, data, current_user)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    db: DbSession,
    data: ProjectUpdate,
    current_user: CurrentWriter,
    project: ProjectWithAccess,
):
    _validate_optional_client_access(db, current_user, data.client_id)
    return project_service.update_project(db, project.id, data, current_user)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    db: DbSession,
    current_user: CurrentWriter,
    project: ProjectWithAccess,
) -> None:
    project_service.delete_project(db, project.id, current_user)


@router.patch("/{project_id}/archive", response_model=ProjectRead)
def archive_project(
    db: DbSession,
    current_user: CurrentWriter,
    project: ProjectWithAccess,
):
    return project_service.archive_project(db, project.id, current_user)


@router.patch("/{project_id}/restore", response_model=ProjectRead)
def restore_project(
    db: DbSession,
    current_user: CurrentWriter,
    project: ProjectWithAccess,
):
    return project_service.restore_project(db, project.id, current_user)
