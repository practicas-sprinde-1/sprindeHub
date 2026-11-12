import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.security.models.user_model import User
from app.security.repositories import user_repo
from app.security.schemas.user_token_schemas import (
    AccessToken,
    AdminUserCreate,
    AdminUserUpdate,
    PasswordChange,
    RefreshTokenRequest,
    Token,
    UserLogin,
    UserRegister,
    UserSelfUpdate,
)
from app.security.utils import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.services import client_service


def _check_email_is_available(
        db: Session,
        email: str,
        current_user: User | None = None,
) -> None:
    if current_user is not None and email == current_user.email:
        return
    if user_repo.find_by_email(db, email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email ya registrado.",
        )


def _check_username_is_available(
        db: Session,
        username: str,
        current_user: User | None = None,
        conflict_detail: str = "Username ya registrado.",
) -> None:
    if current_user is not None and username == current_user.username:
        return
    if user_repo.find_by_username(db, username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=conflict_detail,
        )


def _check_user_is_active(user: User, detail: str) -> None:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


def _decode_refresh_token(refresh_token: str) -> int:
    try:
        token_data = decode_access_token(refresh_token)
        if token_data["token_type"] != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error al refrescar, inicie sesión de nuevo.",
            )
        return int(token_data["sub"])
    except HTTPException:
        raise
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado.",
        )


def _get_validated_updates(
        db: Session,
        data: AdminUserUpdate | UserSelfUpdate,
        user: User,
) -> dict[str, object]:
    updates = data.model_dump(exclude_unset=True, exclude_none=True)

    if "email" in updates:
        _check_email_is_available(db, str(updates["email"]), user)
    if "username" in updates:
        _check_username_is_available(db, str(updates["username"]), user)

    return updates


def _apply_updates(user: User, updates: dict[str, object]) -> None:
    for field, value in updates.items():
        setattr(user, field, value)


def get_user(db: Session, user_id: int) -> User:
    user = user_repo.find_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return user


def get_users_by_id_client(
        db: Session,
        client_id: int,
        offset: int,
        limit: int,
) -> list[User]:
    client_service.get_client(db, client_id)
    return user_repo.find_by_client_id(db, client_id, offset, limit)


def get_users(
        db: Session,
        offset: int,
        limit: int,
        search: str | None = None,
) -> list[User]:
    return user_repo.find_all(db, offset, limit, search)


def get_inactive_users(
        db: Session,
        offset: int,
        limit: int,
) -> list[User]:
    return user_repo.find_all_inactive(db, offset, limit)


def create_user(db: Session, data: UserRegister) -> User:
    email = str(data.email)
    _check_email_is_available(db, email)
    _check_username_is_available(
        db,
        data.username,
        conflict_detail="username ya registrado",
    )

    user = User(
        email=email,
        username=data.username,
        password_hash=hash_password(data.password),
    )
    return user_repo.save(db, user)


def login_user(db: Session, data: UserLogin) -> Token:
    user = user_repo.find_by_email(db, str(data.email))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos.",
        )

    _check_user_is_active(user, "La cuenta está desactivada")
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


def refresh_user(db: Session, data: RefreshTokenRequest) -> AccessToken:
    user_id = _decode_refresh_token(data.refresh_token)
    user = get_user(db, user_id)
    _check_user_is_active(user, "Este usuario está desactivado.")
    return AccessToken(access_token=create_access_token(user_id))


def restore_user(db: Session, user_id: int) -> User:
    user = get_user(db, user_id)
    user.is_active = True
    return user_repo.save(db, user)


def inactive_user(db: Session, user_id: int) -> User:
    user = get_user(db, user_id)
    user.is_active = False
    return user_repo.save(db, user)


def get_active_user(db: Session, user_id: int) -> User:
    user = get_user(db, user_id)
    _check_user_is_active(user, "El usuario está inactivo")
    return user


def update_self_user(
        db: Session,
        user_id: int,
        data: UserSelfUpdate,
) -> User:
    user = get_active_user(db, user_id)
    _apply_updates(user, _get_validated_updates(db, data, user))
    return user_repo.save(db, user)


def change_password(
        db: Session,
        user_id: int,
        data: PasswordChange,
) -> str:
    user = get_active_user(db, user_id)
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta",
        )

    user.password_hash = hash_password(data.new_password)
    user_repo.save(db, user)
    return "Contraseña cambiada"


def admin_create_user(db: Session, data: AdminUserCreate) -> User:
    email = str(data.email)
    _check_email_is_available(db, email)
    _check_username_is_available(
        db,
        data.username,
        conflict_detail="username ya registrado",
    )

    user = User(
        email=email,
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role,
        is_active=data.is_active,
    )
    return user_repo.save(db, user)


def admin_update_user(
        db: Session,
        user_id: int,
        data: AdminUserUpdate,
) -> User:
    user = get_user(db, user_id)
    _apply_updates(user, _get_validated_updates(db, data, user))
    return user_repo.save(db, user)


def admin_delete_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)
    return user_repo.delete(db, user)
