from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.environment import Environment

def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Environment]:
    statement = (
        select(Environment)
        .offset(offset)
        .limit(limit)
        .order_by(Environment.id)
    )
    return list(
        db.scalars(statement).all()
    )

def find_by_id(
        db: Session,
        environment_id: int,
) -> Environment | None:
    return db.get(Environment, environment_id)

def find_by_project_id(
        db: Session,
        project_id: int,
        offset:int=0,
        limit:int=20
) -> list[Environment]:
    statement = (
        select(Environment)
        .where(Environment.project_id == project_id)
        .offset(offset)
        .limit(limit)
        .order_by(Environment.id)
    )

    return list(db.scalars(statement).all())

def save(
        db: Session,
        environment: Environment,

) -> Environment:
    db.add(environment)
    db.commit()
    db.refresh(environment)
    return environment

def delete(
        db: Session,
        environment: Environment,
) -> None:
    db.delete(environment)
    db.commit()

