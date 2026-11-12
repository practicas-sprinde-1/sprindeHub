from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.user_favorite_client_model import UserFavoriteClient
from app.repositories import client_repo, user_favorite_client_repo
from app.schemas.client_schema import (
    ClientCreate,
    ClientLightRead,
    ClientUpdate,
    PaginatedClientRead,
)
from app.security.models.log_model import ActionType, EntityType
from app.security.models.user_model import User
from app.security.services import log_service


def _register_client_log(
    db: Session,
    user_id: int,
    action: ActionType,
    client_id: int,
) -> None:
    log_service.register_log(
        db=db,
        user_id=user_id,
        action=action,
        affected_entity=EntityType.CLIENT,
        affected_entity_id=client_id,
    )


def _save_client_with_log(
    db: Session,
    client: Client,
    user_id: int,
    action: ActionType,
) -> Client:
    try:
        client_repo.save(db, client)
        _register_client_log(db, user_id, action, client.id)
        return _commit_and_refresh_client(db, client)
    except Exception:
        db.rollback()
        raise


def _commit_and_refresh_client(db: Session, client: Client) -> Client:
    try:
        db.commit()
        db.refresh(client)
        return client
    except Exception:
        db.rollback()
        raise


def _validate_unique_name(
    db: Session,
    client: Client,
    name: str | None,
) -> None:
    if not name:
        return

    existing_client = client_repo.find_by_name(db, name)
    if existing_client is None or existing_client.id == client.id:
        return

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Ya existe un cliente con ese nombre",
    )

def _validate_unique_phone(
    db: Session,
    client: Client,
    phone: str | None,
) -> None:
    if not phone:
        return

    existing_client = client_repo.find_by_phone(db, phone)
    if existing_client is None or existing_client.id == client.id:
        return

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Ya existe un cliente con ese telefono",
    )



def _normalize_and_validate_cif(
    db: Session,
    client: Client,
    cif: str,
) -> None:
    if cif == "":
        cif = None

    if cif is None:
        return

    existing_client = client_repo.find_by_cif(db, cif)
    if existing_client is None or existing_client.id == client.id:
        return
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Ya existe un cliente con ese cif",
    )


def _apply_client_updates(client: Client, data: ClientUpdate) -> None:
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(client, field, value)


def _set_client_active_status(
    db: Session,
    client_id: int,
    current_user: User,
    is_active: bool,
) -> Client:
    client = get_client(db, client_id, current_user.id)
    client.is_active = is_active
    return _save_client_with_log(
        db,
        client,
        current_user.id,
        ActionType.UPDATE,
    )


def get_client(
    db: Session,
    client_id: int,
    favorite_user_id: int | None = None,
) -> Client:
    client = client_repo.find_by_id(db, client_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )

    if favorite_user_id is not None:
        client_repo.set_favorite_status(db, client, favorite_user_id)

    return client


def get_clients(
    db: Session,
    offset: int,
    limit: int,
    search: str | None = None,
    favorite_user_id: int | None = None,
) -> PaginatedClientRead:
    return client_repo.find_all(
        db,
        offset,
        limit,
        search,
        favorite_user_id=favorite_user_id,
    )


def get_clients_by_user(
    db: Session,
    user_id: int,
    offset: int,
    limit: int,
    search: str | None = None,
) -> PaginatedClientRead:
    return client_repo.find_all_by_user(db, user_id, offset, limit, search)


def get_clients_light(
    db: Session,
    user_id: int,
) -> list[ClientLightRead]:
    return client_repo.find_all_light(db, user_id)


def get_clients_light_by_user(
    db: Session,
    user_id: int,
) -> list[ClientLightRead]:
    return client_repo.find_all_light_by_user(db, user_id)


def get_archived_clients(
    db: Session,
    offset: int,
    limit: int,
    search: str | None = None,
    favorite_user_id: int | None = None,
) -> PaginatedClientRead:
    return client_repo.find_all_archived(
        db,
        offset,
        limit,
        search,
        favorite_user_id=favorite_user_id,
    )


def get_archived_clients_by_user(
    db: Session,
    user_id: int,
    offset: int,
    limit: int,
    search: str | None = None,
) -> PaginatedClientRead:
    return client_repo.find_all_archived_by_user(
        db,
        user_id,
        offset,
        limit,
        search,
    )


def create_client(
    db: Session,
    data: ClientCreate,
    current_user: User,
) -> Client:
    client = Client(name=data.name, cif=data.cif, phone=data.phone)
    _validate_unique_phone(db,client,client.phone)
    _normalize_and_validate_cif(db,client,client.cif)
    _validate_unique_name(db, client, client.name)

    return _save_client_with_log(
        db,
        client,
        current_user.id,
        ActionType.CREATE,
    )


def update_client(
    db: Session,
    client_id: int,
    data: ClientUpdate,
    current_user: User,
) -> Client:
    client = get_client(db, client_id, current_user.id)
    _validate_unique_name(db, client, data.name)
    _validate_unique_phone(db, client, data.phone)
    _normalize_and_validate_cif(db, client, data.cif)
    _apply_client_updates(client, data)

    return _save_client_with_log(
        db,
        client,
        current_user.id,
        ActionType.UPDATE,
    )


def delete_client(
    db: Session,
    client_id: int,
    current_user: User,
) -> str:
    client = get_client(db, client_id, current_user.id)
    client_name = client.name

    try:
        client_repo.delete(db, client)
        _register_client_log(
            db,
            current_user.id,
            ActionType.DELETE,
            client.id,
        )
        db.commit()
        return f"El cliente '{client_name}' ha sido borrado correctamente"
    except Exception:
        db.rollback()
        raise


def archive_client(
    db: Session,
    client_id: int,
    current_user: User,
) -> Client:
    return _set_client_active_status(
        db,
        client_id,
        current_user,
        is_active=False,
    )


def restore_client(
    db: Session,
    client_id: int,
    current_user: User,
) -> Client:
    return _set_client_active_status(
        db,
        client_id,
        current_user,
        is_active=True,
    )


def get_active_client(db: Session, client_id: int) -> Client:
    client = get_client(db, client_id)
    if client.is_active:
        return client

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="El cliente está archivado",
    )


def favorite_client(
    db: Session,
    client_id: int,
    current_user: User,
) -> Client:
    client = get_client(db, client_id, current_user.id)
    favorite = user_favorite_client_repo.find_by_ids(
        db,
        current_user.id,
        client.id,
    )
    if favorite is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El cliente ya está en favoritos",
        )

    user_favorite_client_repo.save(
        db,
        UserFavoriteClient(user_id=current_user.id, client_id=client.id),
    )
    client.is_favorite = True
    return _commit_and_refresh_client(db, client)


def unfavorite_client(
    db: Session,
    client_id: int,
    current_user: User,
) -> Client:
    client = get_client(db, client_id, current_user.id)
    favorite = user_favorite_client_repo.find_by_ids(
        db,
        current_user.id,
        client.id,
    )
    if favorite is not None:
        user_favorite_client_repo.delete(db, favorite)

    client.is_favorite = False
    return _commit_and_refresh_client(db, client)
