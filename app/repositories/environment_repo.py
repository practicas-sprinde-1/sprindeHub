from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.environment import Environment
from app.models.project import Project
from app.security.models.user_client_model import UserClient


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
def find_all_by_users(
        db: Session,
        user_id:int,
        offset: int = 0,
        limit: int = 20,

) -> list[Environment]:
    statement = (
        select(Environment)
        .join(Project, Project.id == Environment.project_id)
        .join(UserClient, UserClient.client_id == Project.client_id)
        .where(UserClient.user_id==user_id,Project.is_active.is_(True))
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

