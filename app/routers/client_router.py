from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.client import Client
from app.schemas.client_schema import (
    ClientCreate,
    ClientLightRead,
    ClientRead,
    ClientUpdate,
    PaginatedClientRead,
)
from app.schemas.user_favorite_client_schema import (
    UserFavoriteClientAccess,
)
from app.security.dependencies import (
    get_active_current_user,
    require_admin,
    require_client_access,
    require_modifier_role,
)
from app.security.models.user_model import RoleType, User
from app.services import client_service, user_favorite_client_service

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)

#Annotated[TipoDeDato,(Regla-instruccion-etiqueta]
#Depends() -> ejecuta una funcion que devuelve el tipo de dato estipulado
DbSession = Annotated[Session, Depends(get_db)]
ClientWithAccess = Annotated[Client, Depends(require_client_access)]
CurrentWriter = Annotated[User, Depends(require_modifier_role)]
CurrentAdmin = Annotated[User, Depends(require_admin)]
CurrentUser = Annotated[User, Depends(get_active_current_user)]
PaginationOffset = Annotated[int, Query(ge=0)]
PaginationLimit = Annotated[int, Query(ge=1, le=100)]
ClientSearch = Annotated[str | None, Query(min_length=1, max_length=120)]


def _get_accessible_clients(
    db: Session,
    current_user: User,
    offset: int,
    limit: int,
    search: str | None,
) -> PaginatedClientRead:
    if current_user.role != RoleType.ADMIN:
        return client_service.get_clients_by_user(
            db,
            current_user.id,
            offset,
            limit,
            search,
        )

    return client_service.get_clients(
        db,
        offset,
        limit,
        search,
        favorite_user_id=current_user.id,
    )


def _get_accessible_archived_clients(
    db: Session,
    current_user: User,
    offset: int,
    limit: int,
    search: str | None,
) -> PaginatedClientRead:
    if current_user.role != RoleType.ADMIN:
        return client_service.get_archived_clients_by_user(
            db,
            current_user.id,
            offset,
            limit,
            search,
        )

    return client_service.get_archived_clients(
        db,
        offset,
        limit,
        search,
        favorite_user_id=current_user.id,
    )


def _get_accessible_light_clients(
    db: Session,
    current_user: User,
) -> list[ClientLightRead]:
    if current_user.role != RoleType.ADMIN:
        return client_service.get_clients_light_by_user(db, current_user.id)

    return client_service.get_clients_light(db, current_user.id)


def _get_accessible_client(
    db: Session,
    current_user: User,
    client_id: int,
) -> Client:
    client = client_service.get_client(db, client_id)
    require_client_access(client.id, db, current_user)
    return client


@router.get(
    "",
    response_model=PaginatedClientRead,
)
def find_all(
    db: DbSession,
    current_user: CurrentUser,
    offset: PaginationOffset = 0,
    limit: PaginationLimit = 20,
    search: ClientSearch = None,
) -> PaginatedClientRead:
    return _get_accessible_clients(db, current_user, offset, limit, search)


@router.get(
    "/archived",
    response_model=PaginatedClientRead,
)
def find_all_archived(
    db: DbSession,
    current_user: CurrentUser,
    offset: PaginationOffset = 0,
    limit: PaginationLimit = 20,
    search: ClientSearch = None,
) -> PaginatedClientRead:
    return _get_accessible_archived_clients(
        db,
        current_user,
        offset,
        limit,
        search,
    )


@router.get(
    "/light",
    response_model=list[ClientLightRead],
)
def find_all_light(
    db: DbSession,
    current_user: CurrentUser,
) -> list[ClientLightRead]:
    return _get_accessible_light_clients(db, current_user)


@router.get(
    "/favorites",
    response_model=PaginatedClientRead,
)
def find_my_favorites(
    db: DbSession,
    current_user: CurrentUser,
    offset: PaginationOffset = 0,
    limit: PaginationLimit = 20,
    search:str = None,
) -> PaginatedClientRead:
    return user_favorite_client_service.get_user_favorite_clients_by_user_id(
        db, current_user.id, offset, limit,search
    )


@router.patch("/{client_id}/favorite", response_model=ClientRead)
def favorite(
    db: DbSession,
    current_user: CurrentUser,
    favorite_request: Annotated[UserFavoriteClientAccess, Depends()],
) -> Client:
    accessible_client = _get_accessible_client(
        db,
        current_user,
        favorite_request.client_id,
    )
    return client_service.favorite_client(
        db,
        accessible_client.id,
        current_user,
    )


@router.patch("/{client_id}/unfavorite", response_model=ClientRead)
def unfavorite(
    db: DbSession,
    current_user: CurrentUser,
    favorite_request: Annotated[UserFavoriteClientAccess, Depends()],
) -> Client:
    accessible_client = _get_accessible_client(
        db,
        current_user,
        favorite_request.client_id,
    )
    return client_service.unfavorite_client(
        db,
        accessible_client.id,
        current_user,
    )


@router.get(
    "/{client_id}",
    response_model=ClientRead,
)
def find_by_id(
    accessible_client: ClientWithAccess,
) -> Client:
    return accessible_client


@router.post(
    "",
    response_model=ClientRead,
    status_code=status.HTTP_201_CREATED,
)
def create(
    db: DbSession,
    client_data: ClientCreate,
    current_user: CurrentAdmin,
) -> Client:
    return client_service.create_client(db, client_data, current_user)


@router.patch(
    "/{client_id}",
    response_model=ClientRead,
)
def update(
    db: DbSession,
    client_data: ClientUpdate,
    current_user: CurrentWriter,
    accessible_client: ClientWithAccess,
) -> Client:
    return client_service.update_client(
        db,
        accessible_client.id,
        client_data,
        current_user,
    )


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_200_OK,
)
def delete(
    db: DbSession,
    current_user: CurrentWriter,
    accessible_client: ClientWithAccess,
) -> str:
    return client_service.delete_client(db, accessible_client.id, current_user)


@router.patch(
    "/{client_id}/archive",
    response_model=ClientRead,
)
def archive(
    db: DbSession,
    current_user: CurrentWriter,
    accessible_client: ClientWithAccess,
) -> Client:
    return client_service.archive_client(
        db,
        accessible_client.id,
        current_user,
    )


@router.patch(
    "/{client_id}/restore",
    response_model=ClientRead,
)
def restore(
    db: DbSession,
    current_user: CurrentWriter,
    accessible_client: ClientWithAccess,
) -> Client:
    return client_service.restore_client(
        db,
        accessible_client.id,
        current_user,
    )
