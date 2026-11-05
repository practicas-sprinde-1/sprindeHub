from sqlalchemy import select
from sqlalchemy.orm import Session


from app.models.user_favorite_client_model import UserFavoriteClient


def _execute_query(
    db: Session,
    statement,
) -> list[UserFavoriteClient]:
    return list(db.scalars(statement).all())


def find_all(db: Session, offset: int = 0, limit: int = 20) -> list[UserFavoriteClient]:
    statement = select(UserFavoriteClient).offset(offset).limit(limit)
    return _execute_query(db, statement)


def find_by_user_id(
    db: Session,
    user_id: int,
    offset: int = 0,
    limit: int = 20,
) -> list[UserFavoriteClient]:
    statement = (
        select(UserFavoriteClient)
        .where(UserFavoriteClient.user_id == user_id)
        .order_by(UserFavoriteClient.client_id)
        .offset(offset)
        .limit(limit)
    )
    return _execute_query(db, statement)


def find_by_client_id(
    db: Session,
    client_id: int,
    offset: int = 0,
    limit: int = 20,
) -> list[UserFavoriteClient]:
    statement = (
        select(UserFavoriteClient)
        .where(UserFavoriteClient.client_id == client_id)
        .order_by(UserFavoriteClient.user_id)
        .offset(offset)
        .limit(limit)
    )
    return _execute_query(db, statement)


def find_by_ids(
    db: Session,
    user_id: int,
    client_id: int,
) -> UserFavoriteClient | None:
    return db.get(UserFavoriteClient, (user_id, client_id))
