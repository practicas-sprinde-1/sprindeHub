from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.project import Project
from app.security.models.user_client_model import UserClient


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Note]:
    statement = (
        select(Note)
        .offset(offset)
        .limit(limit)
        .order_by(Note.id)
    )
    return list(
        db.scalars(statement).all()
    )

def find_all_by_users(
        db: Session,
        user_id:int,
        offset: int = 0,
        limit: int = 20,

) -> list[Note]:
    statement = (
        select(Note)
        .join(Project, Project.id == Note.project_id)
        .join(UserClient, UserClient.client_id == Project.client_id)
        .where(UserClient.user_id==user_id,Project.is_active.is_(True))
        .offset(offset)
        .limit(limit)
        .order_by(Note.id)
    )
    return list(
        db.scalars(statement).all()
    )


def find_by_id(
        db: Session,
        note_id: int,
) -> Note | None:
    return db.get(Note, note_id)

def find_by_project_id(
        db: Session,
        project_id: int,
        offset:int=0,
        limit:int=20
) -> list[Note]:
    statement = (
        select(Note)
        .where(Note.project_id == project_id)
        .offset(offset)
        .limit(limit)
        .order_by(Note.id)
    )

    return list(db.scalars(statement).all())

def save(
        db: Session,
        note: Note,

) -> Note:
    db.add(note)
    db.flush()
    return note

def delete(
        db: Session,
        note: Note,
) -> None:
    db.delete(note)
