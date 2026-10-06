from fastapi import HTTPException,status
from sqlalchemy.orm import Session

from app.security.models.log_model import Log, ActionType, EntityType
from app.security.repositories import log_repo


def get_log(
        db:Session,
        log_id:int
)->Log:
    log = log_repo.find_by_id(db,log_id)
    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log no encontrado"
        )
    return log

def get_logs(
        db:Session,
        offset:int,
        limit:int
)->list[Log]:
    return log_repo.find_all(db, offset, limit)

def get_logs_by_users(
        db:Session,
        user_id:int,
        offset:int=0,
        limit:int=100
)->list[Log]:
    return log_repo.find_all_by_users(db, user_id, offset, limit)

def get_logs_by_entity(
        db:Session,
        entity_id:int,
        affected_entity:EntityType,
        offset:int,
        limit:int
)->list[Log]:
    return log_repo.find_all_by_entity(db,entity_id,affected_entity,offset,limit)


def register_log(
        db:Session,
        user_id:int,
        action:ActionType,
        affected_entity_id:int,
        affected_entity:EntityType,

)->Log:
    log = Log(
        user_id=user_id,
        action=action,
        affected_entity=affected_entity,
        affected_entity_id=affected_entity_id
    )
    return log_repo.save(db,log)







