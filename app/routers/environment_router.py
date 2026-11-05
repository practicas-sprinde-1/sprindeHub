from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.environment import Environment
from app.models.project import Project
from app.schemas.environment_schema import (
    EnvironmentCreate,
    EnvironmentRead,
    EnvironmentUpdate,
)
from app.security.dependencies import (
    get_active_current_user,
    require_modifier_role,
    require_project_access,
)
from app.security.models.user_model import RoleType, User
from app.services import environment_service

router = APIRouter(prefix="/environments", tags=["environments"])

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_active_current_user)]
CurrentWriter = Annotated[User, Depends(require_modifier_role)]
CurrentProject = Annotated[Project, Depends(require_project_access)]


def _get_accessible_environment(
    db: Session,
    environment_id: int,
    current_user: User,
) -> Environment:
    environment = environment_service.get_environment(db, environment_id)
    require_project_access(environment.project_id, db, current_user)
    return environment

def _validate_optional_project_access(
    db: Session,
    project_id: int | None,
    current_user: User,
) -> None:
    if project_id is None:
        return

    require_project_access(project_id, db, current_user)



@router.get("", response_model=list[EnvironmentRead])
def find_all(
    db: DbSession,
    current_user: CurrentUser,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    if current_user.role != RoleType.ADMIN:
        return environment_service.get_environments_by_users(
            db,
            current_user.id,
            offset,
            limit,
        )

    return environment_service.get_environments(db, offset, limit)


@router.get("/{environment_id}", response_model=EnvironmentRead)
def find_by_id(
    db: DbSession,
    environment_id: int,
    current_user: CurrentUser,
):
    return _get_accessible_environment(db, environment_id, current_user)


@router.get("/project/{project_id}", response_model=list[EnvironmentRead])
def find_by_project_id(
    db: DbSession,
    current_project: CurrentProject,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return environment_service.get_environment_by_id_project(
        db,
        current_project.id,
        offset,
        limit,
    )


@router.post(
    "",
    response_model=EnvironmentRead,
    status_code=status.HTTP_201_CREATED
)
def create(
    db: DbSession,
    data: EnvironmentCreate,
    current_user: CurrentWriter,
):
    require_project_access(data.project_id, db, current_user)
    return environment_service.create_environment(db, data, current_user)


@router.patch(
    "/{environment_id}",
    response_model=EnvironmentRead
)
def update(
    db: DbSession,
    environment_id: int,
    data: EnvironmentUpdate,
    current_user: CurrentWriter,
):
    _get_accessible_environment(db, environment_id, current_user)
    _validate_optional_project_access(db,data.project_id,current_user)
    return environment_service.update_environment(db, environment_id, data, current_user)


@router.delete(
    "/{environment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
    db: DbSession,
    environment_id: int,
    current_user: CurrentWriter,
) -> None:
    _get_accessible_environment(db, environment_id, current_user)
    environment_service.delete_environment(db, environment_id, current_user)
