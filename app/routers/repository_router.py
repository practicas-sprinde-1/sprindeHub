from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.project import Project
from app.schemas.repository_schema import RepositoryRead,RepositoryCreate,RepositoryUpdate
from app.security.dependencies import get_active_current_user, require_project_access, require_modifier_role
from app.security.models.user_model import User, RoleType
from app.services import repository_service

router = APIRouter(
    prefix="/repositories",
    tags=["repositories"]
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
    response_model=list[RepositoryRead]
)
def find_all(
        db:DbSession,
        current_user:CurrentUser,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    if current_user.role == RoleType.ADMIN:
        return repository_service.get_repositories(db,offset,limit)
    return repository_service.get_repositories_by_users(db,current_user.id,offset, limit)

@router.get(
    "/{repository_id}",
    response_model=RepositoryRead
)
def find_by_id(
        db:DbSession,
        repository_id:int,
        current_user:CurrentUser
):
    repository = repository_service.get_repository(db,repository_id)
    require_project_access(repository.project_id,db,current_user)
    return repository

@router.get(
    "/project/{project_id}",
    response_model=list[RepositoryRead]
)
def find_by_project_id(
        db:DbSession,
        current_project:CurrentProject,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return repository_service.get_repository_by_id_project(db,current_project.id,offset,limit)

@router.post(
    "",
    response_model=RepositoryRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: RepositoryCreate,
        current_user:CurrentWriter
):
    require_project_access(data.project_id,db,current_user)
    return repository_service.create_repository(db, data)


@router.patch(
    "/{repository_id}",
    response_model=RepositoryRead
)
def update(
        db: DbSession,
        repository_id: int,
        data: RepositoryUpdate,
        current_user:CurrentWriter
):
    repository = repository_service.get_repository(db,repository_id)
    require_project_access(repository.project_id,db,current_user)

    if data.project_id is not None:
        require_project_access(data.project_id,db,current_user)

    return repository_service.update_repository(db, repository_id, data)


@router.delete(
    "/{repository_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        repository_id: int,
        current_user:CurrentWriter
) -> None:
    repository = repository_service.get_repository(db,repository_id)
    require_project_access(repository.project_id,db,current_user)
    repository_service.delete_repository(db, repository_id)

