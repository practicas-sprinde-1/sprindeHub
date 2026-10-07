from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.project import Project
from app.schemas.domain_schema import DomainRead,DomainCreate,DomainUpdate
from app.security.dependencies import get_active_current_user, require_project_access, require_modifier_role
from app.security.models.user_model import User, RoleType
from app.services import domain_service

router = APIRouter(
    prefix="/domains",
    tags=["domains"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]

CurrentUser = Annotated[
    User,Depends(get_active_current_user)
]

CurrentProject = Annotated[
    Project,Depends(require_project_access)
]

CurrentWriter = Annotated[
    User,Depends(require_modifier_role)
]




@router.get(
    "",
    response_model=list[DomainRead]
)
def find_all(
        db:DbSession,
        current_user:CurrentUser,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)

):
    if current_user.role == RoleType.ADMIN:
        return domain_service.get_domains(db,offset,limit)
    return domain_service.get_domains_by_users(db,current_user.id,offset, limit)

@router.get(
    "/{domain_id}",
    response_model=DomainRead
)
def find_by_id(
        db:DbSession,
        domain_id:int,
        current_user:CurrentUser
):
    domain = domain_service.get_domain(db,domain_id)
    require_project_access(domain.project_id,db,current_user)
    return domain

@router.get(
    "/project/{project_id}",
    response_model=list[DomainRead]
)
def find_by_project_id(
        db:DbSession,
        current_project:CurrentProject,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return domain_service.get_domain_by_id_project(db,current_project.id,offset,limit)

@router.post(
    "",
    response_model=DomainRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: DomainCreate,
        current_user: CurrentWriter,
):
    require_project_access(data.project_id,db,current_user)
    return domain_service.create_domain(db, data,current_user)


@router.patch(
    "/{domain_id}",
    response_model=DomainRead
)
def update(
        db: DbSession,
        domain_id: int,
        data: DomainUpdate,
        current_user:CurrentWriter
):
    domain = domain_service.get_domain(db,domain_id)
    require_project_access(domain.project_id,db,current_user)

    if data.project_id is not None:
        require_project_access(data.project_id, db, current_user)

    return domain_service.update_domain(db, domain_id, data,current_user)

@router.delete(
    "/{domain_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        domain_id: int,
        current_user:CurrentWriter,
) -> None:
    domain = domain_service.get_domain(db,domain_id)
    require_project_access(domain.project_id,db,current_user)
    domain_service.delete_domain(db, domain_id,current_user)

