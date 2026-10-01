from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.schemas.domain_schema import DomainRead,DomainCreate,DomainUpdate
from app.services import domain_service

router = APIRouter(
    prefix="/domains",
    tags=["domains"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]

@router.get(
    "",
    response_model=list[DomainRead]
)
def find_all(
        db:DbSession,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return domain_service.get_domains(db,offset,limit)

@router.get(
    "/{domain_id}",
    response_model=DomainRead
)
def find_by_id(
        db:DbSession,
        domain_id:int
):
    return domain_service.get_domain(db,domain_id)

@router.get(
    "/project/{project_id}",
    response_model=list[DomainRead]
)
def find_by_project_id(
        db:DbSession,
        project_id:int,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return domain_service.get_domain_by_id_project(db,project_id,offset,limit)

@router.post(
    "",
    response_model=DomainRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: DomainCreate
):
    return domain_service.create_domain(db, data)


@router.patch(
    "/{domain_id}",
    response_model=DomainRead
)
def update(
        db: DbSession,
        domain_id: int,
        data: DomainUpdate
):
    return domain_service.update_domain(db, domain_id, data)


@router.delete(
    "/{domain_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        domain_id: int
) -> None:
    domain_service.delete_domain(db, domain_id)

