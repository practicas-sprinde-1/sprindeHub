from sqlalchemy import  select
from sqlalchemy.orm import Session

from app.models.link import Link
from app.models.project import Project
from app.security.models.user_client_model import UserClient


def _find_all(
        db: Session,
        statement,
        offset: int,
        limit: int,
) -> list[Link]:
    paginated_statement = (
        statement
        .order_by(Link.id)
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(paginated_statement).all())


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,
) -> list[Link]:
    return _find_all(db, select(Link), offset, limit)


def find_all_by_users(
        db: Session,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
) -> list[Link]:
    statement = (
        select(Link)
        .join(Project, Project.id == Link.project_id)
        .join(UserClient, UserClient.client_id == Project.client_id)
        .where(UserClient.user_id == user_id, Project.is_active.is_(True))
    )
    return _find_all(db, statement, offset, limit)


def find_by_id(
        db: Session,
        link_id: int,
) -> Link | None:
    return db.get(Link, link_id)


def find_by_project_id(
        db: Session,
        project_id: int,
        offset: int = 0,
        limit: int = 20,
) -> list[Link]:
    statement = select(Link).where(Link.project_id == project_id)
    return _find_all(db, statement, offset, limit)


def save(
        db: Session,
        link: Link,
) -> Link:
    db.add(link)
    db.flush()
    return link


def delete(
        db: Session,
        link: Link,
) -> None:
    db.delete(link)
