from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.client import Client
from app.models.project import Project
from app.security.models.user_client_model import UserClient
from app.security.models.user_model import RoleType, User
from app.security.repositories import user_repo
from app.security.utils import decode_access_token
from app.services import client_service, project_service

bearer_scheme = HTTPBearer(auto_error=False)


def credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _get_user_id(access_token: str) -> int:
    try:
        token_data = decode_access_token(access_token)

        if token_data.get("token_type") != "access":
            raise credentials_exception()

        return int(token_data["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise credentials_exception()


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> User:
    if credentials is None:
        raise credentials_exception()

    user_id = _get_user_id(credentials.credentials)
    user = user_repo.find_by_id(db, user_id)

    if user is None:
        raise credentials_exception()

    return user


def get_active_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta está desactivada.",
        )

    return current_user


def require_admin(
    current_user: Annotated[User, Depends(get_active_current_user)],
) -> User:
    if current_user.role != RoleType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador.",
        )

    return current_user


def require_modifier_role(
    current_user: Annotated[User, Depends(get_active_current_user)],
) -> User:
    if current_user.role not in {RoleType.ADMIN, RoleType.USER}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de escritura y actualizacion.",
        )

    return current_user


def check_client_access(
    db: Session,
    current_user: User,
    client_id: int | None,
) -> None:
    if current_user.role == RoleType.ADMIN:
        return

    if client_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No estás autorizado a acceder a un proyecto sin cliente.",
        )

    user_client = db.get(UserClient, (current_user.id, client_id))

    if user_client is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No estás autorizado a ver los archivos del cliente.",
        )


#Se utiliza como barrera de seguridad para la creacion de tablas hijas
#Antes de crear una tabla hija, se comprueba que el usuario tenga acceso a la tabla padre
#Si es así, devuelve el objeto
def require_client_access(
    client_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_active_current_user)],
) -> Client:
    client = client_service.get_client(db, client_id, current_user.id)
    check_client_access(db, current_user, client.id)

    return client


def require_project_access(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_active_current_user)],
) -> Project:
    project = project_service.get_project(db, project_id, current_user.id)
    check_client_access(db, current_user, project.client_id)

    return project
