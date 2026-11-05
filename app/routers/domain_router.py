from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.domain import Domain
from app.models.project import Project
from app.schemas.domain_schema import DomainCreate, DomainRead, DomainUpdate
from app.security.dependencies import (
    get_active_current_user,
    require_modifier_role,
    require_project_access,
)
from app.security.models.user_model import RoleType, User
from app.services import domain_service

router = APIRouter(prefix="/domains", tags=["domains"])

DbSession = Annotated[Session, Depends(get_db)]
AuthenticatedUser = Annotated[User, Depends(get_active_current_user)]
ProjectWithAccess = Annotated[Project, Depends(require_project_access)]
UserWithWriteAccess = Annotated[User, Depends(require_modifier_role)]


def _get_accessible_domain(
    db: Session,
    domain_id: int,
    current_user: User,
) -> Domain:
    domain = domain_service.get_domain(db, domain_id)
    require_project_access(domain.project_id, db, current_user)
    return domain


def _validate_optional_project_access(
    db: Session,
    project_id: int | None,
    current_user: User,
) -> None:
    if project_id is None:
        return

    require_project_access(project_id, db, current_user)


@router.get("", response_model=list[DomainRead])
def list_domains(
    db: DbSession,
    current_user: AuthenticatedUser,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Domain]:
    if current_user.role == RoleType.ADMIN:
        return domain_service.get_domains(db, offset, limit)

    return domain_service.get_domains_by_users(db, current_user.id, offset, limit)


@router.get("/{domain_id}", response_model=DomainRead)
def get_domain(
    db: DbSession,
    domain_id: int,
    current_user: AuthenticatedUser,
) -> Domain:
    return _get_accessible_domain(db, domain_id, current_user)


@router.get("/project/{project_id}", response_model=list[DomainRead])
def list_project_domains(
    db: DbSession,
    current_project: ProjectWithAccess,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Domain]:
    return domain_service.get_domain_by_id_project(db, current_project.id, offset, limit)


@router.post(
    "",
    response_model=DomainRead,
    status_code=status.HTTP_201_CREATED,
)
def create_domain(
    db: DbSession,
    data: DomainCreate,
    current_user: UserWithWriteAccess,
) -> Domain:
    require_project_access(data.project_id, db, current_user)
    return domain_service.create_domain(db, data, current_user)


@router.patch("/{domain_id}", response_model=DomainRead)
def update_domain(
    db: DbSession,
    domain_id: int,
    data: DomainUpdate,
    current_user: UserWithWriteAccess,
) -> Domain:
    _get_accessible_domain(db, domain_id, current_user)
    _validate_optional_project_access(db, data.project_id, current_user)
    return domain_service.update_domain(db, domain_id, data, current_user)


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_domain(
    db: DbSession,
    domain_id: int,
    current_user: UserWithWriteAccess,
) -> None:
    _get_accessible_domain(db, domain_id, current_user)
    domain_service.delete_domain(db, domain_id, current_user)
