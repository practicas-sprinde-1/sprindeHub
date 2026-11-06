from sqlalchemy import exists, func, or_, select, ColumnElement
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.user_favorite_client_model import UserFavoriteClient
from app.schemas.client_schema import ClientLightRead, PaginatedClientRead
from app.security.models.user_client_model import UserClient


#Metodo auxiliar para ver si un cliente es favorito de un usuario.
#Se utiliza con .select para crear una columna nueva.
def _favorite_query(user_id: int):
    return exists().where(
        UserFavoriteClient.user_id == user_id,
        UserFavoriteClient.client_id == Client.id,
    )


#Metodo auxiliar que filtra los clientes que contienen la palabra buscada
def _client_search_filter(search: str|None):
    search_pattern = f"%{search.strip()}%"
    return or_(
        Client.name.ilike(search_pattern),
        Client.cif.ilike(search_pattern),
        Client.phone.ilike(search_pattern),
    )


# Metodo auxiliar que realiza dos consultas: una para el conteo total de clientes y otra para el listado.
def _prepare_client_list_query(favorite_user_id: int | None):
    if favorite_user_id is not None:
        favorite_status = _favorite_query(favorite_user_id)
    else:
        favorite_status = False

    total_statement = select(func.count(Client.id))

    #En la lista se le añade la columna ('is_favorite'), calculada
    # según el usuario actual, o 'False' por defecto si es None.
    if favorite_user_id is not None:
        clients_statement = select(
            Client,
            favorite_status.label("is_favorite"))

    else:
        clients_statement = select(
            Client,
            favorite_status)

    return total_statement, clients_statement

# Aplica filtros opcionales (estado, favoritos, usuario asignado y búsqueda)
# Acumula las cláusulas WHERE y JOIN según los parámetros recibidos.

def _apply_list_filters(
        total_statement,
        clients_statement,
        is_active: bool | None,
        user_id: int | None,
        search: str | None,
        favorite_user_id: int | None,
        only_favorites: bool,
):
    if is_active is not None:
        active_filter = Client.is_active.is_(is_active)
        total_statement = total_statement.where(active_filter)
        clients_statement = clients_statement.where(active_filter)

    if only_favorites and favorite_user_id is not None:
        favorite_filter = _favorite_query(favorite_user_id)
        total_statement = total_statement.where(favorite_filter)
        clients_statement = clients_statement.where(favorite_filter)

    if user_id is not None:
        total_statement = total_statement.join(
            UserClient,
            UserClient.client_id == Client.id,
        ).where(UserClient.user_id == user_id)
        clients_statement = clients_statement.join(
            UserClient,
            UserClient.client_id == Client.id,
        ).where(UserClient.user_id == user_id)

    if search is not None:
        search_filter = _client_search_filter(search)
        total_statement = total_statement.where(search_filter)
        clients_statement = clients_statement.where(search_filter)

    return total_statement, clients_statement


def _to_paginated_clients(
        rows,
        total: int,
        offset: int,
        limit: int,
) -> PaginatedClientRead:
    clients = []
    #Añade el atributo creado por el metodo auxiliar y lo añade a la instancia cliente
    for client, is_favorite in rows:
        client.is_favorite = bool(is_favorite)
        clients.append(client)

    return PaginatedClientRead(
        items=clients,
        total=total,
        offset=offset,
        limit=limit,
    )


def _find_all(
        db: Session,
        is_active: bool | None,
        offset: int,
        limit: int,
        user_id: int | None = None,
        search: str | None = None,
        favorite_user_id: int | None = None,
        only_favorites: bool = False,
) -> PaginatedClientRead:
    #Prepara la lista de clientes con la columna 'is_favorite'
    total_statement, clients_statement = _prepare_client_list_query(
        favorite_user_id
    )
    #Aplica los filtros a la lista de clientes
    total_statement, clients_statement = _apply_list_filters(
        total_statement,
        clients_statement,
        is_active=is_active,
        user_id=user_id,
        search=search,
        favorite_user_id=favorite_user_id,
        only_favorites=only_favorites,
    )

    #Aplica el conteo total
    total = db.scalar(total_statement) or 0
    # Aplica la paginacion y orden a la consulta
    clients_statement = (
        clients_statement
        .offset(offset)
        .limit(limit)
        .order_by(Client.id)
    )
    #Ejecuta la consulta para obtener los registros
    rows = db.execute(clients_statement).all()

    return _to_paginated_clients(
        rows,
        total=total,
        offset=offset,
        limit=limit,
    )



def _to_light_clients(rows):
    light_clients = []
    for row in rows:
        client = ClientLightRead(
            id=row.id,
            name=row.name,
            is_favorite=row.is_favorite
        )
        light_clients.append(client)
    return light_clients

def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
        favorite_user_id: int | None = None,
) -> PaginatedClientRead:
    return _find_all(
        db,
        is_active=True,
        offset=offset,
        limit=limit,
        search=search,
        favorite_user_id=favorite_user_id,
    )


def find_all_by_user(
        db: Session,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
) -> PaginatedClientRead:
    return _find_all(
        db,
        is_active=True,
        offset=offset,
        limit=limit,
        user_id=user_id,
        search=search,
        favorite_user_id=user_id,
    )


def find_all_archived(
        db: Session,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
        favorite_user_id: int | None = None,
) -> PaginatedClientRead:
    return _find_all(
        db,
        is_active=False,
        offset=offset,
        limit=limit,
        search=search,
        favorite_user_id=favorite_user_id,
    )


def find_all_archived_by_user(
        db: Session,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
) -> PaginatedClientRead:
    return _find_all(
        db,
        is_active=False,
        offset=offset,
        limit=limit,
        user_id=user_id,
        search=search,
        favorite_user_id=user_id,
    )


def find_favorites_by_user(
        db: Session,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
        search:str=None,
) -> PaginatedClientRead:
    return _find_all(
        db,
        is_active=None,
        offset=offset,
        limit=limit,
        search=search,
        favorite_user_id=user_id,
        only_favorites=True,
    )


def find_by_id(db: Session, client_id: int) -> Client | None:
    return db.get(Client, client_id)


def find_by_name(db: Session, client_name: str) -> Client | None:
    statement = select(Client).where(Client.name == client_name)
    return db.scalars(statement).first()


def find_by_cif(db: Session, cif: str) -> Client | None:
    statement = select(Client).where(Client.cif == cif)
    return db.scalars(statement).first()


def set_favorite_status(
        db: Session,
        client: Client,
        user_id: int,
) -> Client:
    favorite_exists = exists().where(
        UserFavoriteClient.user_id == user_id,
        UserFavoriteClient.client_id == client.id,
    )
    client.is_favorite = bool(db.scalar(select(favorite_exists)))
    return client

def find_all_light(
        db: Session,
        user_id: int,
) -> list[ClientLightRead]:
    statement = (
        select(
            Client.id,
            Client.name,
            _favorite_query(user_id).label("is_favorite"),
        )
        .where(Client.is_active.is_(True))
        .order_by(Client.id)
    )
    rows = db.execute(statement).all()
    return _to_light_clients(rows)


def find_all_light_by_user(
        db: Session,
        user_id: int,
) -> list[ClientLightRead]:
    statement = (
        select(
            Client.id,
            Client.name,
            _favorite_query(user_id).label("is_favorite"),
        )
        .join(UserClient, UserClient.client_id == Client.id)
        .where(
            Client.is_active.is_(True),
            UserClient.user_id == user_id,
        )
        .order_by(Client.id)
    )
    rows = db.execute(statement).all()
    return _to_light_clients(rows)


def save(db: Session, client: Client) -> Client:
    if not hasattr(client, "is_favorite"):
        client.is_favorite = False
    db.add(client)
    db.flush()
    return client


def delete(db: Session, client: Client) -> None:
    db.delete(client)
