from sqlalchemy import  select
from sqlalchemy.orm import Session

from app.models.command import Command
from app.models.project import Project
from app.security.models.user_client_model import UserClient


def _find_all(
    db: Session,
    statement,
    offset: int,
    limit: int,
) -> list[Command]:
    paginated_statement = (
        statement
        .offset(offset)
        .limit(limit)
        .order_by(Command.id)
    )
    return list(db.scalars(paginated_statement).all())


def find_all(
    db: Session,
    offset: int = 0,
    limit: int = 20,
) -> list[Command]:
    return _find_all(db, select(Command), offset, limit)


def find_all_by_users(
    db: Session,
    user_id: int,
    offset: int = 0,
    limit: int = 20,
) -> list[Command]:
    statement = (
        select(Command)
        .join(Project, Project.id == Command.project_id)
        .join(UserClient, UserClient.client_id == Project.client_id)
        .where(UserClient.user_id == user_id, Project.is_active.is_(True))
    )
    return _find_all(db, statement, offset, limit)


def find_by_id(
    db: Session,
    command_id: int,
) -> Command | None:
    return db.get(Command, command_id)


def find_by_project_id(
    db: Session,
    project_id: int,
    offset: int = 0,
    limit: int = 20,
) -> list[Command]:
    statement = (
        select(Command)
        .where(Command.project_id == project_id)
    )
    return _find_all(db, statement, offset, limit)


def save(
    db: Session,
    command: Command,
) -> Command:
    db.add(command)
    db.flush()
    return command


def delete(
    db: Session,
    command: Command,
) -> None:
    db.delete(command)
