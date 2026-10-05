from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.security.dependencies import get_active_current_user,require_admin
from app.security.models.user_model import User
from app.security.schemas.user_token_schemas import UserRegister, UserRead, UserLogin, UserSelfUpdate, PasswordChange, \
    AdminUserCreate, AdminUserUpdate, Token
from app.security.services import user_service

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

#Dependencias

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
    response_model= UserRead,
    status_code=status.HTTP_201_CREATED
)
def register(
        db: DbSession,
        data: UserRegister,

):
    return user_service.create_user(db,data)

@router_auth.post(
    "/login",
    response_model=Token,
    status_code = status.HTTP_200_OK
)
def login(
        db:DbSession,
        data:UserLogin
):
    return user_service.login_user(db,data)

@router_users.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK
)
def get_user(
        current_user: CurrentUser,
)->User:
    return current_user


@router_users.patch(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK
)
def update_user(
        db:DbSession,
        current_user: CurrentUser,
        data: UserSelfUpdate
)->User:
    return user_service.update_self_user(db,current_user.id,data)


@router_users.patch(
    "/me/password",
    status_code=status.HTTP_200_OK
)
def change_password(
        db:DbSession,
        current_user:CurrentUser,
        data: PasswordChange
)->str:
    return user_service.change_password(db,current_user.id, data)

@router_admin.get(
    "/users",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK
)
def get_users(
        db:DbSession,
        _:AdminUser,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100)
):
    return user_service.get_users(db,offset, limit)


@router_admin.post(
    "/users",
    response_model=UserRead,
status_code=status.HTTP_201_CREATED
)
def admin_create_user(
        db:DbSession,
        _:AdminUser,
        data:AdminUserCreate
):
    return user_service.admin_create_user(db,data)


@router_admin.patch(
    "/users/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK
)
def admin_update_user(
        db: DbSession,
        _: AdminUser,
        data: AdminUserUpdate,
        user_id:int
):
    return user_service.admin_update_user(db,user_id, data)


