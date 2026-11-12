from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.tag import Tag
from app.security.models.user_client_model import UserClient


def _find_all(
    db: Session,
    statement,
    offset: int,
    limit: int,
) -> list[Tag]:
    statement = statement.order_by(Tag.id).offset(offset).limit(limit)
    return list(db.scalars(statement).all())


def find_all(
    db: Session,
    offset: int = 0,
    limit: int = 20,
) -> list[Tag]:
    return _find_all(db, select(Tag), offset, limit)


def find_all_by_users(
    db: Session,
    user_id: int,
    offset: int = 0,
    limit: int = 20,
) -> list[Tag]:
    statement = (
        select(Tag)
        .join(Client, Client.id == Tag.client_id)
        .join(UserClient, UserClient.client_id == Client.id)
        .where(UserClient.user_id == user_id, Client.is_active.is_(True))
    )
    return _find_all(db, statement, offset, limit)


def find_by_id(db: Session, tag_id: int) -> Tag | None:
    return db.get(Tag, tag_id)


def find_by_client_id(
    db: Session,
    client_id: int,
    offset: int = 0,
    limit: int = 20,
) -> list[Tag]:
    statement = select(Tag).where(Tag.client_id == client_id)
    return _find_all(db, statement, offset, limit)


def save(db: Session, tag: Tag) -> Tag:
    db.add(tag)
    db.flush()
    return tag


def delete(db: Session, tag: Tag) -> None:
    db.delete(tag)
