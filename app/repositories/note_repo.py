from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.note import Note

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
    db.commit()
    db.refresh(note)
    return note

def delete(
        db: Session,
        note: Note,
) -> None:
    db.delete(note)
    db.commit()
