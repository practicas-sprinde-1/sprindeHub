from sqlalchemy import select
from sqlalchemy.orm import Session

from app.security.models.user_client_model import UserClient
from app.security.models.user_model import User


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[User]:
    statement = (
        select(User)
        .where(User.is_active.is_(True))
        .offset(offset)
        .limit(limit)
        .order_by(User.id)
    )
    return list(
        db.scalars(statement).all()
    )


def find_all_inactive(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[User]:
    statement = (
        select(User)
        .where(User.is_active.is_(False))
        .offset(offset)
        .limit(limit)
        .order_by(User.id)
    )
    return list(
        db.scalars(statement).all()
    )


def find_by_id(
        db: Session,
        user_id: int,
) -> User | None:
    return db.get(User, user_id)


def find_by_email(
        db: Session,
        email: str,
) -> User | None:
    statement = (
        select(User)
        .where(User.email == email)
    )
    return db.scalar(statement)


def find_by_username(
        db: Session,
        username: str,
) -> User | None:
    statement = (
        select(User)
        .where(User.username == username)
    )
    return db.scalar(statement)


def find_by_client_id(
        db: Session,
        client_id: int,
        offset: int = 0,
        limit: int = 20
) -> list[User]:
    statement = (
        select(User)
        .join(UserClient, UserClient.user_id == User.id)
        .where(UserClient.client_id == client_id, User.is_active.is_(True))
        .offset(offset)
        .limit(limit)
        .order_by(User.id)
    )

    return list(db.scalars(statement).all())


def save(
        db: Session,
        user: User,

) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
