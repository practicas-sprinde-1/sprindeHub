from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.security.dependencies import get_active_current_user, require_admin
from app.security.models.log_model import Log, EntityType
from app.security.models.user_client_model import UserClient
from app.security.models.user_model import User
from app.security.schemas.log_schema import LogRead
from app.security.schemas.userClient_schema import UserClientRead, UserClientAccess
from app.security.schemas.user_token_schemas import UserRegister, UserRead, UserLogin, UserSelfUpdate, PasswordChange, \
    AdminUserCreate, AdminUserUpdate, Token
from app.security.services import user_service, user_client_service, log_service

router_auth = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

router_users = APIRouter(
    prefix="/users",
    tags=["users"]
)

router_admin = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# Dependencias

DbSession = Annotated[
    Session,
    Depends(get_db)
]

CurrentUser = Annotated[
    User,
    Depends(get_active_current_user),
]

AdminUser = Annotated[
    User,
    Depends(require_admin)
]


@router_auth.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
def register(
        db: DbSession,
        data: UserRegister,

):
    return user_service.create_user(db, data)


@router_auth.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
def login(
        db: DbSession,
        data: UserLogin
):
    return user_service.login_user(db, data)


@router_users.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK
)
def get_user(
        current_user: CurrentUser,
) -> User:
    return current_user


@router_users.patch(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK
)
def update_user(
        db: DbSession,
        current_user: CurrentUser,
        data: UserSelfUpdate
) -> User:
    return user_service.update_self_user(db, current_user.id, data)


@router_users.patch(
    "/me/password",
    status_code=status.HTTP_200_OK
)
def change_password(
        db: DbSession,
        current_user: CurrentUser,
        data: PasswordChange
) -> str:
    return user_service.change_password(db, current_user.id, data)


@router_admin.get(
    "/users",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK
)
def get_users(
        db: DbSession,
        _: AdminUser,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100)
):
    return user_service.get_users(db, offset, limit)


@router_admin.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
def admin_create_user(
        db: DbSession,
        _: AdminUser,
        data: AdminUserCreate
):
    return user_service.admin_create_user(db, data)


@router_admin.patch(
    "/users/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK
)
def admin_update_user(
        db: DbSession,
        _: AdminUser,
        data: AdminUserUpdate,
        user_id: int
):
    return user_service.admin_update_user(db, user_id, data)


@router_admin.post(
    "/user-clients/users/{user_id}/clients",
    response_model=UserClientRead,
    status_code=status.HTTP_201_CREATED
)
def assign_user_to_client(
        db: DbSession,
        user_id: int,
        _: AdminUser,
        data: UserClientAccess
) -> UserClient:
    return user_client_service.assign_user_to_client(db, user_id, data)


@router_admin.get(
    "/user-clients/",
    response_model=UserClientRead,
    status_code=status.HTTP_200_OK
)
def get_user_client(
        db: DbSession,
        user_id: int,
        client_id: int,
        _: AdminUser
) -> UserClient:
    return user_client_service.get_user_client(db, user_id, client_id)


@router_admin.delete(
    "/user-clients/users/{user_id}/clients/{client_id}",
    status_code=status.HTTP_200_OK
)
def revoke_client_access(
        db: DbSession,
        user_id: int,
        client_id: int,
        _: AdminUser
) -> str:
    return user_client_service.revoke_client_access(db, user_id, client_id)


@router_admin.get(
    "/user-clients/clients/{client_id}/users",
    response_model=list[UserClientRead],
    status_code=status.HTTP_200_OK
)
def get_user_client_by_client_id(
        db: DbSession,
        client_id: int,
        _: AdminUser,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100),
) -> list[UserClient]:
    return user_client_service.get_user_clients_by_client_id(db, client_id, offset, limit)


@router_admin.get(
    "/user-clients/{user_id}",
    response_model=list[UserClientRead],
    status_code=status.HTTP_200_OK
)
def get_user_client_by_user_id(
        db: DbSession,
        user_id: int,
        _: AdminUser,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100),
) -> list[UserClient]:
    return user_client_service.get_user_clients_by_user_id(db, user_id, offset, limit)


@router_admin.get(
    "/logs",
    response_model=list[LogRead],
    status_code=status.HTTP_200_OK
)
def get_logs(
        db: DbSession,
        _: AdminUser,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100)
) -> list[Log]:
    return log_service.get_logs(db, offset, limit)


@router_admin.get(
    "/logs/{log_id}",
    response_model=LogRead,
    status_code=status.HTTP_200_OK
)
def get_log_by_id(
        db: DbSession,
        _: AdminUser,
        log_id: int
) -> Log:
    return log_service.get_log(db, log_id)


@router_admin.get(
    "/logs/users/{user_id}",
    response_model=list[LogRead],
    status_code=status.HTTP_200_OK
)
def get_logs_by_user_id(
        db: DbSession,
        _: AdminUser,
        user_id: int,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100)
) -> list[Log]:
    return log_service.get_logs_by_users(db, user_id, offset, limit)

@router_admin.get(
    "/logs/entities/{affected_entity}/{entity_id}",
    response_model=list[LogRead],
    status_code=status.HTTP_200_OK
)
def get_logs_by_entity_type_and_id(
        db: DbSession,
        _: AdminUser,
        entity_id: int,
        affected_entity:EntityType,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100)
) -> list[Log]:
    return log_service.get_logs_by_entity(db, entity_id,affected_entity, offset, limit)

