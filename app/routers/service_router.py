from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.project import Project
from app.models.service import Service
from app.schemas.service_schema import ServiceCreate, ServiceRead, ServiceUpdate
from app.security.dependencies import (
    get_active_current_user,
    require_modifier_role,
    require_project_access,
)
from app.security.models.user_model import RoleType, User
from app.services import service_table_service

router = APIRouter(prefix="/services", tags=["services"])

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_active_current_user)]
CurrentWriter = Annotated[User, Depends(require_modifier_role)]
CurrentProject = Annotated[Project, Depends(require_project_access)]


def _get_accessible_service(
    db: Session,
    service_id: int,
    current_user: User,
) -> Service:
    service = service_table_service.get_service(db, service_id)
    require_project_access(service.project_id, db, current_user)
    return service

def _validate_optional_project_access(
    db: Session,
    project_id: int | None,
    current_user: User,
) -> None:
    if project_id is None:
        return

    require_project_access(project_id, db, current_user)

@router.get("", response_model=list[ServiceRead])
def list_services(
    db: DbSession,
    current_user: CurrentUser,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Service]:
    if current_user.role == RoleType.ADMIN:
        return service_table_service.get_services(db, offset, limit)

    return service_table_service.get_services_by_users(db, current_user.id, offset, limit)


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(
    db: DbSession,
    service_id: int,
    current_user: CurrentUser,
) -> Service:
    return _get_accessible_service(db, service_id, current_user)


@router.get("/project/{project_id}", response_model=list[ServiceRead])
def list_project_services(
    db: DbSession,
    current_project: CurrentProject,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Service]:
    return service_table_service.get_service_by_id_project(
        db,
        current_project.id,
        offset,
        limit,
    )


@router.post(
    "",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    db: DbSession,
    data: ServiceCreate,
    current_user: CurrentWriter,
) -> Service:
    require_project_access(data.project_id, db, current_user)
    return service_table_service.create_service(db, data, current_user)


@router.patch("/{service_id}", response_model=ServiceRead)
def update_service(
    db: DbSession,
    service_id: int,
    data: ServiceUpdate,
    current_user: CurrentWriter,
) -> Service:
    _get_accessible_service(db, service_id, current_user)

    _validate_optional_project_access(db,data.project_id,current_user)


    return service_table_service.update_service(db, service_id, data, current_user)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    db: DbSession,
    service_id: int,
    current_user: CurrentWriter,
) -> None:
    _get_accessible_service(db, service_id, current_user)
    service_table_service.delete_service(db, service_id, current_user)
