from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.client import Client
from app.schemas.client_schema import ClientRead, ClientCreate, ClientUpdate
from app.security.dependencies import require_client_access, require_modifier_role, require_admin, \
    get_active_current_user
from app.security.models.user_model import User, RoleType
from app.services import client_service

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]

ClientWithAccess = Annotated[
    Client,Depends(require_client_access)
]

CurrentWriter = Annotated[
    User, Depends(require_modifier_role)
]

CurrentAdmin = Annotated[
    User, Depends(require_admin)
]

CurrentUser = Annotated[
    User,
    Depends(get_active_current_user),
]




@router.get(
    "",
    response_model=list[ClientRead]
)
def find_all(
        db: DbSession,
        user:CurrentUser,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100),
):
    if user.role == RoleType.ADMIN:
        return client_service.get_clients(db, offset, limit)

    return client_service.get_clients_by_user(db,user.id,offset, limit)


@router.get(
    "/{client_id}",
    response_model=ClientRead
)
def find_by_id(
        client:ClientWithAccess
):
    return client


@router.post(
    "",
    response_model=ClientRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: ClientCreate,
        _:CurrentAdmin,
):
    return client_service.create_client(db, data)


@router.patch(
    "/{client_id}",
    response_model=ClientRead
)
def update(
        db: DbSession,
        data: ClientUpdate,
        _:CurrentWriter,
        client:ClientWithAccess,
):
    return client_service.update_client(db, client.id, data)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        _: CurrentWriter,
        client: ClientWithAccess,
) -> None:
    client_service.delete_client(db, client.id)


@router.patch(
    "/{client_id}/archive",
    response_model=ClientRead
)
def archive(
        db: DbSession,
        _: CurrentWriter,
        client: ClientWithAccess,
):
    return client_service.archive_client(db, client.id)



@router.patch(
    "/{client_id}/restore",
    response_model=ClientRead
)
def restore(
        db: DbSession,
        _: CurrentWriter,
        client: ClientWithAccess,
):
    return client_service.restore_client(db, client.id)