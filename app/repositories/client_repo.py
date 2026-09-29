from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[Client]:
    statement = (
        select(Client)
        .offset(offset)
        .limit(limit)
    )
    return list(
        db.scalars(statement).all()
    )


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
    db.commit()
    db.refresh(client)
    return client


def delete(
        db: Session,
        client: Client,
) -> None:
    db.delete(client)
    db.commit()
