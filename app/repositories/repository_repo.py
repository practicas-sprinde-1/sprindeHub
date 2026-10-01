from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.repository import Repository

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
    db.commit()
    db.refresh(repository)
    return repository

def delete(
        db: Session,
        repository: Repository,
) -> None:
    db.delete(repository)
    db.commit()
