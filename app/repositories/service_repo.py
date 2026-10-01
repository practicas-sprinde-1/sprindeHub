from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service import Service

def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Service]:
    statement = (
        select(Service)
        .offset(offset)
        .limit(limit)
        .order_by(Service.id)
    )
    return list(
        db.scalars(statement).all()
    )

def find_by_id(
        db: Session,
        service_id: int,
) -> Service | None:
    return db.get(Service, service_id)

def find_by_project_id(
        db: Session,
        project_id: int,
        offset:int=0,
        limit:int=20
) -> list[Service]:
    statement = (
        select(Service)
        .where(Service.project_id == project_id)
        .offset(offset)
        .limit(limit)
        .order_by(Service.id)
    )

    return list(db.scalars(statement).all())

def save(
        db: Session,
        service: Service,

) -> Service:
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

def delete(
        db: Session,
        service: Service,
) -> None:
    db.delete(service)
    db.commit()
