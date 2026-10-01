from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.schemas.service_schema import ServiceRead,ServiceCreate,ServiceUpdate
from app.services import service_table_service

router = APIRouter(
    prefix="/services",
    tags=["services"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]

@router.get(
    "",
    response_model=list[ServiceRead]
)
def find_all(
        db:DbSession,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return service_table_service.get_services(db,offset,limit)

@router.get(
    "/{service_id}",
    response_model=ServiceRead
)
def find_by_id(
        db:DbSession,
        service_id:int
):
    return service_table_service.get_service(db,service_id)

@router.get(
    "/project/{project_id}",
    response_model=list[ServiceRead]
)
def find_by_project_id(
        db:DbSession,
        project_id:int,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return service_table_service.get_service_by_id_project(db,project_id,offset,limit)

@router.post(
    "",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: ServiceCreate
):
    return service_table_service.create_service(db, data)


@router.patch(
    "/{service_id}",
    response_model=ServiceRead
)
def update(
        db: DbSession,
        service_id: int,
        data: ServiceUpdate
):
    return service_table_service.update_service(db, service_id, data)


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        service_id: int
) -> None:
    service_table_service.delete_service(db, service_id)

