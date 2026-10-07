from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.repository import Repository
from app.security.models.user_client_model import UserClient


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Repository]:
    statement = (
        select(Repository)
        .offset(offset)
        .limit(limit)
        .order_by(Repository.id)
    )
    return list(
        db.scalars(statement).all()
    )

def find_all_by_users(
        db: Session,
        user_id:int,
        offset: int = 0,
        limit: int = 20,

) -> list[Repository]:
    statement = (
        select(Repository)
        .join(Project,Project.id==Repository.project_id)
        .join(UserClient,UserClient.client_id==Project.client_id)
        .where(UserClient.user_id==user_id,Project.is_active.is_(True))
        .offset(offset)
        .limit(limit)
        .order_by(Repository.id)
    )
    return list(
        db.scalars(statement).all()
    )

def find_by_id(
        db: Session,
        repository_id: int,
) -> Repository | None:
    return db.get(Repository, repository_id)

def find_by_project_id(
        db: Session,
        project_id: int,
        offset:int=0,
        limit:int=20
) -> list[Repository]:
    statement = (
        select(Repository)
        .where(Repository.project_id == project_id)
        .offset(offset)
        .limit(limit)
        .order_by(Repository.id)
    )

    return list(db.scalars(statement).all())

def save(
        db: Session,
        repository: Repository,

) -> Repository:
    db.add(repository)
    db.flush()
    return repository

def delete(
        db: Session,
        repository: Repository,
) -> None:
    db.delete(repository)
