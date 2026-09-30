from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.schemas.environment_schema import EnvironmentUpdate,EnvironmentCreate,EnvironmentRead
from app.services import environment_service

router = APIRouter(
    prefix="/environments",
    tags=["environments"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]

@router.get(
    "",
    response_model=list[EnvironmentRead]
)
def find_all(
        db:DbSession,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return environment_service.get_environments(db,offset,limit)

@router.get(
    "/{environment_id}",
    response_model=EnvironmentRead
)
def find_by_id(
        db:DbSession,
        environment_id:int
):
    return environment_service.get_environment(db,environment_id)

@router.get(
    "/project/{project_id}",
    response_model=list[EnvironmentRead]
)
def find_by_project_id(
        db:DbSession,
        project_id:int,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return environment_service.get_environment_by_id_project(db,project_id,offset,limit)

@router.post(
    "",
    response_model=EnvironmentRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: EnvironmentCreate
):
    return environment_service.create_environment(db, data)


@router.patch(
    "/{environment_id}",
    response_model=EnvironmentRead
)
def update(
        db: DbSession,
        environment_id: int,
        data: EnvironmentUpdate
):
    return environment_service.update_environment(db, environment_id, data)


@router.delete(
    "/{environment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        environment_id: int
) -> None:
    environment_service.delete_environment(db, environment_id)

