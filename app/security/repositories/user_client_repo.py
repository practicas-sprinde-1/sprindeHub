from sqlalchemy import select
from sqlalchemy.orm import Session

from app.security.models.user_client_model import UserClient

def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,

) -> list[UserClient]:
    statement = (
        select(UserClient)
        .offset(offset)
        .limit(limit)
    )
    return list(
        db.scalars(statement).all()
    )

def find_by_user_id(
        db: Session,
        user_id: int,
        offset:int=0,
        limit:int=20

) -> list[UserClient]:
    statement = (
        select(UserClient)
        .where(UserClient.user_id==user_id)
        .offset(offset)
        .limit(limit)
        .order_by(UserClient.client_id)
    )
    return list(
        db.scalars(statement).all()
    )


def find_by_client_id(
        db: Session,
        client_id: int,
        offset: int = 0,
        limit: int = 20

) -> list[UserClient]:
    statement = (
        select(UserClient)
        .where(UserClient.client_id==client_id)
        .offset(offset)
        .limit(limit)
        .order_by(UserClient.user_id)
    )
    return list(
        db.scalars(statement).all()
    )

def find_by_ids(
        db:Session,
        user_id:int,
        client_id:int
)->UserClient | None:
    statement = (
        select(UserClient)
        .where(UserClient.client_id == client_id, UserClient.user_id==user_id)
    )

    return db.scalar(statement)



def save(
        db: Session,
        user_client: UserClient,

) -> UserClient:
    db.add(user_client)
    db.commit()
    db.refresh(user_client)
    return user_client


def delete(
        db:Session,
        user_client:UserClient
)->None:
    db.delete(user_client)
    db.commit()


