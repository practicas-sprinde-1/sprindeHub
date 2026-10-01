from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.command import Command

def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Command]:
    statement = (
        select(Command)
        .offset(offset)
        .limit(limit)
        .order_by(Command.id)
    )
    return list(
        db.scalars(statement).all()
    )

def find_by_id(
        db: Session,
        commands_id: int,
) -> Command | None:
    return db.get(Command, commands_id)

def find_by_project_id(
        db: Session,
        project_id: int,
        offset:int=0,
        limit:int=20
) -> list[Command]:
    statement = (
        select(Command)
        .where(Command.project_id == project_id)
        .offset(offset)
        .limit(limit)
        .order_by(Command.id)
    )

    return list(db.scalars(statement).all())

def save(
        db: Session,
        commands: Command,

) -> Command:
    db.add(commands)
    db.commit()
    db.refresh(commands)
    return commands

def delete(
        db: Session,
        commands: Command,
) -> None:
    db.delete(commands)
    db.commit()
