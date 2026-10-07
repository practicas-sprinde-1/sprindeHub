from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.project import Project
from app.schemas.command_schema import CommandRead,CommandCreate,CommandUpdate
from app.security.dependencies import get_active_current_user, require_project_access, require_modifier_role
from app.security.models.user_model import User, RoleType
from app.services import command_service

router = APIRouter(
    prefix="/commands",
    tags=["commands"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]

CurrentUser = Annotated[
    User, Depends(get_active_current_user)
]

CurrentWriter = Annotated[
    User,Depends(require_modifier_role)
]

CurrentProject = Annotated[
    Project,Depends(require_project_access)
]

@router.get(
    "",
    response_model=list[CommandRead]
)
def find_all(
        db:DbSession,
        current_user:CurrentUser,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    if current_user.role == RoleType.ADMIN:
        return command_service.get_commands(db, offset, limit)

    return command_service.get_commands_by_users(db,current_user.id,offset, limit)

@router.get(
    "/{command_id}",
    response_model=CommandRead
)
def find_by_id(
        db:DbSession,
        command_id:int,
        current_user:CurrentUser

):
    command = command_service.get_command(db, command_id)
    require_project_access(command.project_id,db,current_user)
    return command


@router.get(
    "/project/{project_id}",
    response_model=list[CommandRead]
)
def find_by_project_id(
        db:DbSession,
        current_project:CurrentProject,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return command_service.get_commands_by_id_project(db,current_project.id,offset,limit)

@router.post(
    "",
    response_model=CommandRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: CommandCreate,
        current_user:CurrentWriter
):
    require_project_access(data.project_id,db,current_user)
    return command_service.create_command(db, data,current_user)


@router.patch(
    "/{command_id}",
    response_model=CommandRead
)
def update(
        db: DbSession,
        command_id: int,
        data: CommandUpdate,
        current_user:CurrentWriter
):
    command = command_service.get_command(db, command_id)
    require_project_access(command.project_id, db, current_user)

    if data.project_id is not None:
        require_project_access(data.project_id, db, current_user)

    return command_service.update_command(db, command_id, data,current_user)


@router.delete(
    "/{command_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        command_id: int,
        current_user:CurrentWriter
) -> None:
    command = command_service.get_command(db,command_id)
    require_project_access(command.project_id, db, current_user)
    command_service.delete_command(db, command_id,current_user)

