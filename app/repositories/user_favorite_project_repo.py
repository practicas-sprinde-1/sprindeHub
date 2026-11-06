from sqlalchemy import  select
from sqlalchemy.orm import Session

from app.models.user_favorite_project_model import UserFavoriteProject


def _execute_query(
    db: Session, statement
) -> list[UserFavoriteProject]:
    return list(db.scalars(statement).all())


def find_all(
    db: Session, offset: int = 0, limit: int = 20
) -> list[UserFavoriteProject]:
    statement = select(UserFavoriteProject).offset(offset).limit(limit)
    return _execute_query(db, statement)


def find_by_user_id(
    db: Session, user_id: int, offset: int = 0, limit: int = 20
) -> list[UserFavoriteProject]:
    statement = (
        select(UserFavoriteProject)
        .where(UserFavoriteProject.user_id == user_id)
        .offset(offset)
        .limit(limit)
        .order_by(UserFavoriteProject.project_id)
    )
    return _execute_query(db, statement)


def find_by_project_id(
    db: Session, project_id: int, offset: int = 0, limit: int = 20
) -> list[UserFavoriteProject]:
    statement = (
        select(UserFavoriteProject)
        .where(UserFavoriteProject.project_id == project_id)
        .offset(offset)
        .limit(limit)
        .order_by(UserFavoriteProject.user_id)
    )
    return _execute_query(db, statement)


def find_by_ids(
    db: Session, user_id: int, project_id: int
) -> UserFavoriteProject | None:
    return db.get(UserFavoriteProject, (user_id, project_id))


def save(
    db: Session,
    favorite: UserFavoriteProject,
) -> UserFavoriteProject:
    db.add(favorite)
    db.flush()
    return favorite


def delete(
    db: Session,
    favorite: UserFavoriteProject,
) -> None:
    db.delete(favorite)
