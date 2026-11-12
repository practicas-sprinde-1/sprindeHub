from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.link import Link
from app.models.project import Project
from app.schemas.link_schema import LinkCreate, LinkRead, LinkUpdate
from app.security.dependencies import (
    get_active_current_user,
    require_modifier_role,
    require_project_access,
)
from app.security.models.user_model import RoleType, User
from app.services import link_service

router = APIRouter(
    prefix="/links",
    tags=["links"],
)

DbSession = Annotated[
    Session,
    Depends(get_db),
]

CurrentUser = Annotated[
    User,
    Depends(get_active_current_user),
]

CurrentModifier = Annotated[
    User,
    Depends(require_modifier_role),
]

AccessibleProject = Annotated[
    Project,
    Depends(require_project_access),
]


def _get_accessible_link(
    db: Session,
    link_id: int,
    current_user: User,
) -> Link:
    link = link_service.get_link(db, link_id)
    require_project_access(link.project_id, db, current_user)
    return link


def _validate_optional_project_access(
    db: Session,
    project_id: int | None,
    current_user: User,
) -> None:
    if project_id is None:
        return

    require_project_access(project_id, db, current_user)


@router.get("", response_model=list[LinkRead])
def find_all(
    db: DbSession,
    current_user: CurrentUser,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Link]:
    if current_user.role == RoleType.ADMIN:
        return link_service.get_links(db, offset, limit)

    return link_service.get_links_by_users(db, current_user.id, offset, limit)


@router.get("/{link_id}", response_model=LinkRead)
def find_by_id(
    db: DbSession,
    link_id: int,
    current_user: CurrentUser,
) -> Link:
    return _get_accessible_link(db, link_id, current_user)


@router.get(
    "/project/{project_id}",
    response_model=list[LinkRead],
)
def find_by_project_id(
    db: DbSession,
    current_project: AccessibleProject,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Link]:
    return link_service.get_link_by_id_project(db, current_project.id, offset, limit)


@router.post(
    "",
    response_model=LinkRead,
    status_code=status.HTTP_201_CREATED,
)
def create(
    db: DbSession,
    link_data: LinkCreate,
    current_user: CurrentModifier,
) -> Link:
    require_project_access(link_data.project_id, db, current_user)
    return link_service.create_link(db, link_data, current_user)


@router.patch(
    "/{link_id}",
    response_model=LinkRead,
)
def update(
    db: DbSession,
    link_id: int,
    link_data: LinkUpdate,
    current_user: CurrentModifier,
) -> Link:
    _get_accessible_link(db, link_id, current_user)
    _validate_optional_project_access(db, link_data.project_id, current_user)

    return link_service.update_link(db, link_id, link_data, current_user)


@router.delete(
    "/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    db: DbSession,
    link_id: int,
    current_user: CurrentModifier,
) -> None:
    _get_accessible_link(db, link_id, current_user)
    link_service.delete_link(db, link_id, current_user)
