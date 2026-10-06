from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.command import Command
from app.models.project import Project
from app.security.models.user_client_model import UserClient


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

def find_all_by_users(
        db: Session,
        user_id:int,
        offset: int = 0,
        limit: int = 20,

) -> list[Command]:
    statement = (
        select(Command)
        .join(Project,Project.id==Command.project_id)
        .join(UserClient,UserClient.client_id==Project.client_id)
        .where(UserClient.user_id==user_id,Project.is_active.is_(True))
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
