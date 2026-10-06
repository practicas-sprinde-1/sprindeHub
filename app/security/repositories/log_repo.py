from sqlalchemy import select
from sqlalchemy.orm import Session

from app.security.models.log_model import Log, EntityType


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Log]:
    statement = (
        select(Log)
        .offset(offset)
        .limit(limit)
        .order_by(Log.created_at.desc())
    )
    return list(
        db.scalars(statement).all()
    )
def find_all_by_users(
        db: Session,
        user_id:int,
        offset: int = 0,
        limit: int = 20,

) -> list[Log]:
    statement = (
        select(Log)
        .where(Log.user_id==user_id)
        .offset(offset)
        .limit(limit)
        .order_by(Log.created_at.desc())
    )
    return list(
        db.scalars(statement).all()
    )

def find_all_by_entity(
        db: Session,
        entity_id:int,
        affected_entity:EntityType,
        offset: int = 0,
        limit: int = 20,

) -> list[Log]:
    statement = (
        select(Log)
        .where(Log.affected_entity_id==entity_id,Log.affected_entity==affected_entity)
        .offset(offset)
        .limit(limit)
        .order_by(Log.created_at.desc())
    )
    return list(
        db.scalars(statement).all()
    )


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
