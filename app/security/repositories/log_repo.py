from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.security.models.log_model import EntityType, Log
from app.security.models.user_model import User


def _filter_by_search(
        statement,
        search: str | None,
):
    if search is None or not search.strip():
        return statement

    pattern = f"%{search.strip()}%"
    return (
        statement
        .join(User, User.id == Log.user_id)
        .where(
            or_(
                User.username.ilike(pattern),
                Log.search_text.ilike(pattern),
            )
        )
    )


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
):
    statement = _filter_by_search(select(Log), search)
    statement = (
        statement
        .order_by(Log.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def find_all_by_users(
        db: Session,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
) -> list[Log]:
    statement = (
        select(Log)
        .where(Log.user_id == user_id)
        .order_by(Log.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def find_all_by_entity(
        db: Session,
        entity_id: int,
        affected_entity: EntityType,
        offset: int = 0,
        limit: int = 20,
) -> list[Log]:
    statement = (
        select(Log)
        .where(Log.affected_entity_id == entity_id, Log.affected_entity == affected_entity)
        .order_by(Log.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def find_by_id(
        db: Session,
        log_id: int,
) -> Log | None:
    return db.get(Log, log_id)


def save(
        db: Session,
        log: Log,
) -> Log:
    db.add(log)
    db.flush()
    return log
