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

def get_clients_by_user(
        db: Session,
        user_id:int,
        offset:int,
        limit:int
)->list[Client]:
    return client_repo.find_all_by_user(db, user_id, offset, limit)

def get_archived_clients(
        db: Session,
        offset: int,
        limit: int
) -> list[Client]:
    return client_repo.find_all_archived(db, offset, limit)



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
    client_name= client.name
    client_repo.delete(db, client)
    return f"El cliente '{client_name}' ha sido borrado correctamente"

def archive_client(
        db: Session,
        client_id: int,
) -> Client:
    client = get_client(db, client_id)

    client.is_active = False

    return client_repo.save(db, client)

def restore_client(
        db: Session,
        client_id: int,
) -> Client:
    client = get_client(db, client_id)

    client.is_active = True

    return client_repo.save(db, client)

def get_active_client(db: Session, client_id: int) -> Client:
    client = get_client(db, client_id)

    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El cliente está archivado",
        )

    return client