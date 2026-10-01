from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.link import Link

def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Link]:
    statement = (
        select(Link)
        .offset(offset)
        .limit(limit)
        .order_by(Link.id)
    )
    return list(
        db.scalars(statement).all()
    )

def find_by_id(
        db: Session,
        link_id: int,
) -> Link | None:
    return db.get(Link, link_id)

def find_by_project_id(
        db: Session,
        project_id: int,
        offset:int=0,
        limit:int=20
) -> list[Link]:
    statement = (
        select(Link)
        .where(Link.project_id == project_id)
        .offset(offset)
        .limit(limit)
        .order_by(Link.id)
    )

    return list(db.scalars(statement).all())

def save(
        db: Session,
        link: Link,

) -> Link:
    db.add(link)
    db.commit()
    db.refresh(link)
    return link

def delete(
        db: Session,
        link: Link,
) -> None:
    db.delete(link)
    db.commit()
