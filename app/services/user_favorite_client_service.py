from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_favorite_client_model import UserFavoriteClient
from app.repositories import user_favorite_client_repo, client_repo
from app.schemas.client_schema import PaginatedClientRead
from app.schemas.user_favorite_client_schema import UserFavoriteClientAccess
from app.security.services import user_service
from app.services import client_service


def get_user_favorite_client(
        db: Session, user_id: int, client_id: int
) -> UserFavoriteClient:
    favorite = user_favorite_client_repo.find_by_ids(db, user_id, client_id)
    if favorite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorito no encontrado")
    return favorite


def get_user_favorite_clients(
        db: Session, offset: int, limit: int
) -> list[UserFavoriteClient]:
    return user_favorite_client_repo.find_all(db, offset, limit)


def get_user_favorite_clients_by_user_id(
        db: Session, user_id: int, offset: int, limit: int,search:str
) -> PaginatedClientRead:
    user_service.get_user(db, user_id)
    return client_repo.find_favorites_by_user(db, user_id, offset, limit,search)


def get_user_favorite_clients_by_client_id(
        db: Session, client_id: int, offset: int, limit: int
) -> list[UserFavoriteClient]:
    client_service.get_client(db, client_id)
    return user_favorite_client_repo.find_by_client_id(db, client_id, offset, limit)


def assign_user_favorite_client(
        db: Session, user_id: int, data: UserFavoriteClientAccess
) -> UserFavoriteClient:
    user = user_service.get_user(db, user_id)
    client = client_service.get_client(db, data.client_id)
    if user_favorite_client_repo.find_by_ids(db, user.id, client.id) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El cliente {client.name} ya está en favoritos.",
        )
    client_service.favorite_client(db, client.id, user)
    return get_user_favorite_client(db, user.id, client.id)


def revoke_user_favorite_client(db: Session, user_id: int, client_id: int) -> str:
    user = user_service.get_user(db, user_id)
    client = client_service.get_client(db, client_id)
    if user_favorite_client_repo.find_by_ids(db, user.id, client.id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El cliente {client.name} no está en favoritos.",
        )
    client_service.unfavorite_client(db, client.id, user)
    return f"El cliente {client.name} eliminado de favoritos correctamente."
