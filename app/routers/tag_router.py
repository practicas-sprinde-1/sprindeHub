from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import DbSession
from app.models.client import Client
from app.models.tag import Tag
from app.schemas.tag_schema import (
    TagCreate,
    TagRead,
    TagUpdate,
)
from app.security.dependencies import (
    get_active_current_user,
    require_client_access,
    require_modifier_role,
)
from app.security.models.user_model import RoleType, User
from app.services import tag_service

router = APIRouter(prefix="/tags", tags=["tags"])

CurrentUser = Annotated[User, Depends(get_active_current_user)]
CurrentWriter = Annotated[User, Depends(require_modifier_role)]
ClientWithAccess = Annotated[Client, Depends(require_client_access)]
PaginationOffset = Annotated[int, Query(ge=0)]
PaginationLimit = Annotated[int, Query(ge=1, le=100)]


def _get_accessible_tag(
    db: Session,
    tag_id: int,
    current_user: User,
) -> Tag:
    tag = tag_service.get_tag(db, tag_id)
    require_client_access(tag.client_id, db, current_user)
    return tag


@router.get("", response_model=list[TagRead])
def list_tags(
    db: DbSession,
    current_user: CurrentUser,
    offset: PaginationOffset = 0,
    limit: PaginationLimit = 20,
) -> list[Tag]:
    if current_user.role == RoleType.ADMIN:
        return tag_service.get_tags(db, offset, limit)

    return tag_service.get_tags_by_users(
        db, current_user.id, offset, limit,
    )


@router.get("/client/{client_id}", response_model=list[TagRead])
def list_tags_by_client(
    db: DbSession,
    client: ClientWithAccess,
    offset: PaginationOffset = 0,
    limit: PaginationLimit = 20,
) -> list[Tag]:
    return tag_service.get_tags_by_client(
        db, client.id, offset, limit,
    )


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(
    db: DbSession,
    tag_id: int,
    current_user: CurrentUser,
) -> Tag:
    return _get_accessible_tag(db, tag_id, current_user)


@router.post(
    "",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un tag del cliente",
)
def create_tag(
    db: DbSession,
    data: TagCreate,
    current_user: CurrentWriter,
) -> Tag:
    require_client_access(data.client_id, db, current_user)
    return tag_service.create_tag(db, data, current_user)


@router.patch(
    "/{tag_id}",
    response_model=TagRead,
    summary="Actualizar los datos del tag, incluida su MAC o IP",
)
def update_tag(
    db: DbSession,
    tag_id: int,
    data: TagUpdate,
    current_user: CurrentWriter,
) -> Tag:
    tag = _get_accessible_tag(db, tag_id, current_user)
    return tag_service.update_tag(db, tag.id, data, current_user)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    db: DbSession,
    tag_id: int,
    current_user: CurrentWriter,
) -> None:
    tag = _get_accessible_tag(db, tag_id, current_user)
    tag_service.delete_tag(db, tag.id, current_user)
