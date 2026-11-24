from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.tag import Tag
from app.security.models.user_client_model import UserClient


def _apply_tag_search(statement, search: str | None):
    if not search:
        return statement

    search_pattern = f"%{search.strip()}%"
    return statement.where(
        or_(
            Tag.tag_type.ilike(search_pattern),
            Tag.brand.ilike(search_pattern),
            Tag.model.ilike(search_pattern),
            Tag.mac.ilike(search_pattern),
            Tag.ip.ilike(search_pattern),
        )
    )


def _find_all(
    db: Session,
    statement,
    offset: int,
    limit: int,
    search: str | None = None,
) -> list[Tag]:
    statement = _apply_tag_search(statement, search)
    statement = statement.order_by(Tag.id).offset(offset).limit(limit)
    return list(db.scalars(statement).all())


def find_all(
    db: Session,
    offset: int = 0,
    limit: int = 20,
    search: str | None = None,
) -> list[Tag]:
    return _find_all(db, select(Tag), offset, limit, search)


def find_all_by_users(
    db: Session,
    user_id: int,
    offset: int = 0,
    limit: int = 20,
    search: str | None = None,
) -> list[Tag]:
    statement = (
        select(Tag)
        .join(Client, Client.id == Tag.client_id)
        .join(UserClient, UserClient.client_id == Client.id)
        .where(UserClient.user_id == user_id, Client.is_active.is_(True))
    )
    return _find_all(db, statement, offset, limit, search)


def find_by_id(db: Session, tag_id: int) -> Tag | None:
    return db.get(Tag, tag_id)


def find_by_client_id(
    db: Session,
    client_id: int,
    offset: int = 0,
    limit: int = 20,
    search: str | None = None,
) -> list[Tag]:
    statement = select(Tag).where(Tag.client_id == client_id)
    return _find_all(db, statement, offset, limit, search)


def save(db: Session, tag: Tag) -> Tag:
    db.add(tag)
    db.flush()
    return tag


def delete(db: Session, tag: Tag) -> None:
    db.delete(tag)
