from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.schemas.link_schema import LinkRead,LinkCreate,LinkUpdate
from app.services import link_service

router = APIRouter(
    prefix="/links",
    tags=["links"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]

@router.get(
    "",
    response_model=list[LinkRead]
)
def find_all(
        db:DbSession,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return link_service.get_links(db,offset,limit)

@router.get(
    "/{link_id}",
    response_model=LinkRead
)
def find_by_id(
        db:DbSession,
        link_id:int
):
    return link_service.get_link(db,link_id)

@router.get(
    "/project/{project_id}",
    response_model=list[LinkRead]
)
def find_by_project_id(
        db:DbSession,
        project_id:int,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return link_service.get_link_by_id_project(db,project_id,offset,limit)

@router.post(
    "",
    response_model=LinkRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: LinkCreate
):
    return link_service.create_link(db, data)


@router.patch(
    "/{link_id}",
    response_model=LinkRead
)
def update(
        db: DbSession,
        link_id: int,
        data: LinkUpdate
):
    return link_service.update_link(db, link_id, data)


@router.delete(
    "/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        link_id: int
) -> None:
    link_service.delete_link(db, link_id)

