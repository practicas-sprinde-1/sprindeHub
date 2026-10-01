from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.schemas.repository_schema import RepositoryRead,RepositoryCreate,RepositoryUpdate
from app.services import repository_service

router = APIRouter(
    prefix="/repositories",
    tags=["repositories"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]

@router.get(
    "",
    response_model=list[RepositoryRead]
)
def find_all(
        db:DbSession,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return repository_service.get_repositories(db,offset,limit)

@router.get(
    "/{repository_id}",
    response_model=RepositoryRead
)
def find_by_id(
        db:DbSession,
        repository_id:int
):
    return repository_service.get_repository(db,repository_id)

@router.get(
    "/project/{project_id}",
    response_model=list[RepositoryRead]
)
def find_by_project_id(
        db:DbSession,
        project_id:int,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return repository_service.get_repository_by_id_project(db,project_id,offset,limit)

@router.post(
    "",
    response_model=RepositoryRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: RepositoryCreate
):
    return repository_service.create_repository(db, data)


@router.patch(
    "/{repository_id}",
    response_model=RepositoryRead
)
def update(
        db: DbSession,
        repository_id: int,
        data: RepositoryUpdate
):
    return repository_service.update_repository(db, repository_id, data)


@router.delete(
    "/{repository_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        repository_id: int
) -> None:
    repository_service.delete_repository(db, repository_id)

