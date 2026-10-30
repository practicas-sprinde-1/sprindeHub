from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client_schema import ClientLightRead, PaginatedClientRead
from app.security.models.user_client_model import UserClient


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
) -> PaginatedClientRead:
    return _find_all(
        db, is_active=True, offset=offset, limit=limit, search=search
    )


def find_all_by_user(
        db: Session,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
) -> PaginatedClientRead:
    return _find_all(
        db, is_active=True, offset=offset, limit=limit, user_id=user_id,
        search=search,
    )


def find_all_archived(
        db: Session,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
) -> PaginatedClientRead:
    return _find_all(
        db, is_active=False, offset=offset, limit=limit, search=search
    )


def find_all_archived_by_user(
        db: Session,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
) -> PaginatedClientRead:
    return _find_all(
        db, is_active=False, offset=offset, limit=limit, user_id=user_id,
        search=search,
    )


def _find_all(
        db: Session,
        is_active: bool,
        offset: int,
        limit: int,
        user_id: int | None = None,
        search: str | None = None,
) -> PaginatedClientRead:
    total_statement = (
        select(func.count(Client.id))
        .where(Client.is_active.is_(is_active))
    )

    statement = select(Client).where(Client.is_active.is_(is_active))

    if user_id is not None:
        total_statement = total_statement.join(
            UserClient, UserClient.client_id == Client.id
        ).where(UserClient.user_id == user_id)
        statement = statement.join(
            UserClient, UserClient.client_id == Client.id
        ).where(UserClient.user_id == user_id)

    if search is not None:
        pattern = f"%{search.strip()}%"
        search_filter = or_(
            Client.name.ilike(pattern),
            Client.cif.ilike(pattern),
            Client.phone.ilike(pattern),
        )
        total_statement = total_statement.where(search_filter)
        statement = statement.where(search_filter)

    total = db.scalar(total_statement) or 0
    statement = (
        statement
        .offset(offset)
        .limit(limit)
        .order_by(Client.id)
    )

    return PaginatedClientRead(
        items=list(db.scalars(statement).all()),
        total=total,
        offset=offset,
        limit=limit,
    )


def find_by_id(
        db: Session,
        client_id: int,
) -> Client | None:
    return db.get(Client, client_id)

def find_by_name(
        db: Session,
        client_name: str,
) -> Client | None:
    stmt = select(Client).where(Client.name == client_name)
    return db.scalars(stmt).first()

def find_by_cif(
        db: Session,
        cif: str,
) -> Client | None:
    stmt = select(Client).where(Client.cif == cif)
    return db.scalars(stmt).first()


def find_all_light(
        db: Session,
) -> list[ClientLightRead]:
    statement = (
        select(Client)
        .where(Client.is_active.is_(True))
        .order_by(Client.id)
    )

    clients = db.scalars(statement).all()

    clients_light = []

    for client in clients:
        client_light = ClientLightRead(
            id=client.id,
            name=client.name,
        )
        clients_light.append(client_light)

    return clients_light


def find_all_light_by_user(
        db: Session,
        user_id: int,
) -> list[ClientLightRead]:
    statement = (
        select(Client.id, Client.name)
        .join(UserClient, UserClient.client_id == Client.id)
        .where(
            Client.is_active.is_(True),
            UserClient.user_id == user_id,
        )
        .order_by(Client.id)
    )

    clients = db.execute(statement).all()

    clients_light = []

    for client in clients:
        client_light = ClientLightRead(
            id=client.id,
            name=client.name,
        )
        clients_light.append(client_light)

    return clients_light


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
