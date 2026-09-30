from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.schemas.project_schema import ProjectCreate,ProjectUpdate,ProjectRead
from app.services import project_service

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

DbSession= Annotated[
    Session,
    Depends(get_db)
]

@router.get(
    "",
    response_model=list[ProjectRead]
)
def find_all(
        db:DbSession,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return project_service.get_projects(db,offset,limit)

@router.get(
    "/{project_id}",
    response_model=ProjectRead
)
def find_by_id(
        db:DbSession,
        project_id:int
):
    return project_service.get_project(db,project_id)

@router.get(
    "/client/{client_id}",
    response_model=list[ProjectRead]
)
def find_by_client_id(
        db:DbSession,
        client_id:int,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return project_service.get_projects_by_id_client(db,client_id,offset,limit)

@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: ProjectCreate
):
    return project_service.create_project(db, data)


@router.patch(
    "/{project_id}",
    response_model=ProjectRead
)
def update(
        db: DbSession,
        project_id: int,
        data: ProjectUpdate
):
    return project_service.update_project(db, project_id, data)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        project_id: int
) -> None:
    project_service.delete_project(db, project_id)


@router.patch(
    "/{project_id}/archive",
    response_model=ProjectRead
)
def archive(
        db:DbSession,
        project_id:int
):
    return project_service.archive_project(db,project_id)


@router.patch(
    "/{project_id}/restore",
    response_model=ProjectRead
)
def restore(
        db:DbSession,
        project_id:int
):
    return project_service.restore_project(db,project_id)



