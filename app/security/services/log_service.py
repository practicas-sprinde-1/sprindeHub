from datetime import date, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.command import Command
from app.models.domain import Domain
from app.models.environment import Environment
from app.models.link import Link
from app.models.note import Note
from app.models.project import Project
from app.models.repository import Repository
from app.models.service import Service
from app.security.models.log_model import Log, ActionType, EntityType, utc_now_db
from app.security.repositories import log_repo
from app.security.schemas.log_schema import LogPage


ENTITY_TEXT_VALUE = {
    EntityType.CLIENT: (Client, "name"),
    EntityType.COMMAND: (Command, "name"),
    EntityType.DOMAIN: (Domain, "url"),
    EntityType.ENVIRONMENT: (Environment, "url"),
    EntityType.LINK: (Link, "title"),
    EntityType.NOTE: (Note, "description"),
    EntityType.PROJECT: (Project, "name"),
    EntityType.REPOSITORY: (Repository, "url"),
    EntityType.SERVICE: (Service, "name"),
}


def _get_entity_text(
        db: Session,
        entity_id: int,
        entity_type: EntityType,
) -> object:
    #Desempaqueta la tupla del diccionario, entity_model = entidad y field_name = atributo
    entity_model, field_name = ENTITY_TEXT_VALUE[entity_type]

    #Evita que se borre la entidad sin antes haber guardado su valor
    with db.no_autoflush:
        entity = db.get(entity_model, entity_id)

    if entity is None:
        return ""
    #Usa "" para evitar que salte error en caso de poner un campo/atributo que no existe y devuelva "".
    return getattr(entity,field_name,"")


def _format_for_search(
        action: ActionType,
        entity_type: EntityType,
        created_at: datetime,
        entity_value: object,
) -> str:
    return f"{action.value} {entity_type.value} {created_at.isoformat(sep=' ')} {entity_value}"


def get_log(
        db: Session,
        log_id: int
) -> Log:
    log = log_repo.find_by_id(db, log_id)
    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log no encontrado"
        )
    return log


def get_logs(
        db: Session,
        offset: int,
        limit: int,
        search: str | None = None,
) -> list[Log]:
    return log_repo.find_all_list(db, offset, limit, search)


def get_logs_page(
        db: Session,
        *,
        offset: int,
        limit: int,
        start_date: date | None = None,
        end_date: date | None = None,
        action: ActionType | None = None,
        username: str | None = None,
        affected_entity: EntityType | None = None,
        search: str | None = None,
) -> LogPage:
    if start_date is not None and end_date is not None:
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="start_date debe ser anterior o igual a end_date.",
            )

    end_before = None
    if end_date is not None and end_date < date.max:
        end_before = end_date + timedelta(days=1)

    return log_repo.find_all(
        db,
        offset=offset,
        limit=limit,
        start_date=start_date,
        end_before=end_before,
        action=action,
        username=username,
        affected_entity=affected_entity,
        search=search,
    )


def get_logs_by_users(
        db: Session,
        user_id: int,
        offset: int = 0,
        limit: int = 100
) -> list[Log]:
    return log_repo.find_all_by_users(db, user_id, offset, limit)


def get_logs_by_entity(
        db: Session,
        entity_id: int,
        affected_entity: EntityType,
        offset: int,
        limit: int
) -> list[Log]:
    return log_repo.find_all_by_entity(db, entity_id, affected_entity, offset, limit)


def register_log(
        db: Session,
        user_id: int,
        action: ActionType,
        affected_entity_id: int,
        affected_entity: EntityType,

) -> Log:
    created_at = utc_now_db()
    entity_value = _get_entity_text(
        db,
        affected_entity_id,
        affected_entity,
    )
    search_text = _format_for_search(
        action,
        affected_entity,
        created_at,
        entity_value,
    )

    log = Log(
        user_id=user_id,
        action=action,
        affected_entity=affected_entity,
        affected_entity_id=affected_entity_id,
        search_text=search_text,
        created_at=created_at,
    )
    return log_repo.save(db, log)
