from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.command import Command
from app.models.project import Project
from app.schemas.command_schema import CommandCreate, CommandRead, CommandUpdate
from app.security.dependencies import (
    get_active_current_user,
    require_modifier_role,
    require_project_access,
)
from app.security.models.user_model import RoleType, User
from app.services import command_service

router = APIRouter(prefix="/commands", tags=["commands"])

DbSession = Annotated[Session, Depends(get_db)]
AuthenticatedUser = Annotated[User, Depends(get_active_current_user)]
CommandWriter = Annotated[User, Depends(require_modifier_role)]
AccessibleProject = Annotated[Project, Depends(require_project_access)]


def _get_accessible_command(
    db: Session,
    command_id: int,
    current_user: User,
) -> Command:
    command = command_service.get_command(db, command_id)
    require_project_access(command.project_id, db, current_user)
    return command


def _validate_optional_project_access(
    db: Session,
    project_id: int | None,
    current_user: User,
) -> None:
    if project_id is None:
        return

    require_project_access(project_id, db, current_user)


@router.get("", response_model=list[CommandRead], name="find_all")
def find_all_commands(
    db: DbSession,
    current_user: AuthenticatedUser,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Command]:
    if current_user.role == RoleType.ADMIN:
        return command_service.get_commands(db, offset, limit)

    return command_service.get_commands_by_users(db, current_user.id, offset, limit)


@router.get("/{command_id}", response_model=CommandRead, name="find_by_id")
def find_command_by_id(
    db: DbSession,
    command_id: int,
    current_user: AuthenticatedUser,
) -> Command:
    return _get_accessible_command(db, command_id, current_user)


@router.get(
    "/project/{project_id}",
    response_model=list[CommandRead],
    name="find_by_project_id",
)
def find_commands_by_project_id(
    db: DbSession,
    current_project: AccessibleProject,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Command]:
    return command_service.get_commands_by_id_project(
        db,
        current_project.id,
        offset,
        limit,
    )


@router.post(
    "",
    response_model=CommandRead,
    status_code=status.HTTP_201_CREATED,
    name="create",
)
def create_command(
    db: DbSession,
    command_data: CommandCreate,
    current_user: CommandWriter,
) -> Command:
    require_project_access(command_data.project_id, db, current_user)
    return command_service.create_command(db, command_data, current_user)


@router.patch("/{command_id}", response_model=CommandRead, name="update")
def update_command(
    db: DbSession,
    command_id: int,
    command_data: CommandUpdate,
    current_user: CommandWriter,
) -> Command:
    _get_accessible_command(db, command_id, current_user)
    _validate_optional_project_access(
        db,
        command_data.project_id,
        current_user,
    )
    return command_service.update_command(
        db,
        command_id,
        command_data,
        current_user,
    )


@router.delete(
    "/{command_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete",
)
def delete_command(
    db: DbSession,
    command_id: int,
    current_user: CommandWriter,
) -> None:
    _get_accessible_command(db, command_id, current_user)
    command_service.delete_command(db, command_id, current_user)
