from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.project import Project
from app.schemas.service_schema import ServiceRead,ServiceCreate,ServiceUpdate
from app.security.dependencies import get_active_current_user, require_project_access, require_modifier_role
from app.security.models.user_model import User, RoleType
from app.services import service_table_service

router = APIRouter(
    prefix="/services",
    tags=["services"]
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
    response_model=list[ServiceRead]
)
def find_all(
        db:DbSession,
        current_user:CurrentUser,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    if current_user.role == RoleType.ADMIN:
        return service_table_service.get_services(db,offset,limit)
    return service_table_service.get_services_by_users(db,current_user.id,offset, limit)

@router.get(
    "/{service_id}",
    response_model=ServiceRead
)
def find_by_id(
        db:DbSession,
        service_id:int,
        current_user:CurrentUser
):
    service = service_table_service.get_service(db,service_id)
    require_project_access(service.project_id,db,current_user)
    return service

@router.get(
    "/project/{project_id}",
    response_model=list[ServiceRead]
)
def find_by_project_id(
        db:DbSession,
        current_project:CurrentProject,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return service_table_service.get_service_by_id_project(db,current_project.id,offset,limit)

@router.post(
    "",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: ServiceCreate,
        current_user:CurrentWriter
):
    require_project_access(data.project_id,db,current_user)
    return service_table_service.create_service(db, data)


@router.patch(
    "/{service_id}",
    response_model=ServiceRead
)
def update(
        db: DbSession,
        service_id: int,
        data: ServiceUpdate,
        current_user:CurrentWriter
):
    service = service_table_service.get_service(db,service_id)
    require_project_access(service.project_id,db,current_user)

    if data.project_id is not None:
        require_project_access(data.project_id,db,current_user)

    return service_table_service.update_service(db, service_id, data)


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        service_id: int,
        current_user:CurrentWriter
) -> None:
    service = service_table_service.get_service(db,service_id)
    require_project_access(service.project_id,db,current_user)
    service_table_service.delete_service(db, service_id)

