from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.schemas.command_schema import CommandRead,CommandCreate,CommandUpdate
from app.services import command_service

router = APIRouter(
    prefix="/commands",
    tags=["commands"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]

@router.get(
    "",
    response_model=list[CommandRead]
)
def find_all(
        db:DbSession,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return command_service.get_commands(db,offset,limit)

@router.get(
    "/{command_id}",
    response_model=CommandRead
)
def find_by_id(
        db:DbSession,
        command_id:int
):
    return command_service.get_command(db,command_id)

@router.get(
    "/project/{project_id}",
    response_model=list[CommandRead]
)
def find_by_project_id(
        db:DbSession,
        project_id:int,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return command_service.get_commands_by_id_project(db,project_id,offset,limit)

@router.post(
    "",
    response_model=CommandRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: CommandCreate
):
    return command_service.create_command(db, data)


@router.patch(
    "/{command_id}",
    response_model=CommandRead
)
def update(
        db: DbSession,
        command_id: int,
        data: CommandUpdate
):
    return command_service.update_command(db, command_id, data)


@router.delete(
    "/{command_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        command_id: int
) -> None:
    command_service.delete_command(db, command_id)

