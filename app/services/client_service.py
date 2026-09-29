from fastapi import HTTPException,status

from sqlalchemy.orm import Session

from app.models.client import Client

from app.repositories import client_repo


def get_client(
        db:Session,
        client_id:int
)->Client:
    client = client_repo.find_by_id(
        db,
        client_id
    )
    if client is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client

def get_clients(
        db:Session,
        offset:int,
        limit:int
)->list[Client]:

    clients = client_repo.find_all(db,offset,limit)

    if clients is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="Clients not found"
        )
    return clients

def create_client