from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.repositories import client_repo
from app.schemas.client_schema import ClientCreate, ClientUpdate


def get_client(
        db: Session,
        client_id: int
) -> Client:
    client = client_repo.find_by_id(
        db,
        client_id
    )
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return client


def get_clients(
        db: Session,
        offset: int,
        limit: int
) -> list[Client]:
    return client_repo.find_all(db, offset, limit)


def create_client(
        db: Session,
        data: ClientCreate,
) -> Client:
    client = Client(
        name=data.name,
        cif=data.cif,
        phone=data.phone
    )

    return client_repo.save(db, client)


def update_client(
        db: Session,
        client_id: int,
        data: ClientUpdate
) -> Client:
    client = get_client(
        db, client_id
    )

    updates = data.model_dump(
        exclude_unset=True
    )

    for field, value in updates.items():
        setattr(client, field, value)

    return client_repo.save(db,client)


def delete_client(
        db: Session,
        client_id: int
) -> str:
    client = get_client(db, client_id)
    client_repo.delete(db, client)
    return f"El cliente '{client.name}' ha sido borrado correctamente"
