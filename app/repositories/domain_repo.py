from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Domain

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
    db.commit()
    db.refresh(domain)
    return domain

def delete(
        db: Session,
        domain: Domain,
) -> None:
    db.delete(domain)
    db.commit()
