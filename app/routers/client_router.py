from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.schemas.client_schema import ClientRead, ClientCreate, ClientUpdate
from app.services import client_service

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]


@router.get(
    "",
    response_model=list[ClientRead]
)
def find_all(
        db: DbSession,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100)
):
    return client_service.get_clients(db, offset, limit)


@router.get(
    "/{client_id}",
    response_model=ClientRead
)
def find_by_id(
        db: DbSession,
        client_id: int
):
    return client_service.get_client(db, client_id)


@router.post(
    "",
    response_model=ClientRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: ClientCreate
):
    return client_service.create_client(db, data)


@router.patch(
    "/{client_id}",
    response_model=ClientRead
)
def update(
        db: DbSession,
        client_id: int,
        data: ClientUpdate
):
    return client_service.update_client(db, client_id, data)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        client_id: int
) -> None:
    client_service.delete_client(db, client_id)
