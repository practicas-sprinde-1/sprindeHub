from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.security.models.user_client_model import UserClient


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Client]:
    statement = (
        select(Client)
        .where(Client.is_active.is_(True))
        .offset(offset)
        .limit(limit)
        .order_by(Client.id)
    )
    return list(
        db.scalars(statement).all()
    )
def find_all_by_user(
        db: Session,
        user_id: int,
        offset: int = 0,
        limit: int = 20,

) -> list[Client]:
    statement = (
        select(Client)
        .join(UserClient, UserClient.client_id==Client.id)
        .where(UserClient.user_id==user_id, Client.is_active.is_(True))
        .offset(offset)
        .limit(limit)
        .order_by(Client.id)
    )
    return list(
        db.scalars(statement).all()
    )

def find_all_archived(
        db: Session,
        offset: int = 0,
        limit: int = 20,
) -> list[Client]:
    statement = (
        select(Client)
        .where(Client.is_active.is_(False))
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def find_by_id(
        db: Session,
        client_id: int,
) -> Client | None:
    return db.get(Client, client_id)


def save(
        db: Session,
        client: Client,

) -> Client:
    db.add(client)
    db.flush()
    return client


def delete(
        db: Session,
        client: Client,
) -> None:
    db.delete(client)
