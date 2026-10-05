from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Project]:
    statement = (
        select(Project)
        .where(Project.is_active.is_(True))
        .offset(offset)
        .limit(limit)
        .order_by(Project.id)
    )
    return list(
        db.scalars(statement).all()
    )

def find_all_archived(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Project]:
    statement = (
        select(Project)
        .where(Project.is_active.is_(False))
        .offset(offset)
        .limit(limit)
        .order_by(Project.id)
    )
    return list(
        db.scalars(statement).all()
    )



def find_by_id(
        db: Session,
        project_id: int,
) -> Project | None:
    return db.get(Project, project_id)


def find_by_client_id(
        db: Session,
        client_id: int,
        offset:int=0,
        limit:int=20
) -> list[Project]:
    statement = (
        select(Project)
        .where(Project.client_id == client_id)
        .offset(offset)
        .limit(limit)
        .order_by(Project.id)
    )

    return list(db.scalars(statement).all())



def save(
        db: Session,
        project: Project,

) -> Project:
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def delete(
        db: Session,
        project: Project,
) -> None:
    db.delete(project)
    db.commit()
