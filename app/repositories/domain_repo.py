from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Domain
from app.models.project import Project
from app.security.models.user_client_model import UserClient


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Domain]:
    statement = (
        select(Domain)
        .offset(offset)
        .limit(limit)
        .order_by(Domain.id)
    )
    return list(
        db.scalars(statement).all()
    )

def find_all_by_users(
        db: Session,
        user_id:int,
        offset: int = 0,
        limit: int = 20,

) -> list[Domain]:
    statement = (
        select(Domain)
        .join(Project, Project.id == Domain.project_id)
        .join(UserClient, UserClient.client_id == Project.client_id)
        .where(UserClient.user_id==user_id,Project.is_active.is_(True))
        .offset(offset)
        .limit(limit)
        .order_by(Domain.id)
    )
    return list(
        db.scalars(statement).all()
    )

def find_by_id(
        db: Session,
        domain_id: int,
) -> Domain | None:
    return db.get(Domain, domain_id)

def find_by_project_id(
        db: Session,
        project_id: int,
        offset:int=0,
        limit:int=20
) -> list[Domain]:
    statement = (
        select(Domain)
        .where(Domain.project_id == project_id)
        .offset(offset)
        .limit(limit)
        .order_by(Domain.id)
    )

    return list(db.scalars(statement).all())

def save(
        db: Session,
        domain: Domain,

) -> Domain:
    db.add(domain)
    db.flush()
    return domain

def delete(
        db: Session,
        domain: Domain,
) -> None:
    db.delete(domain)
