from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.repositories import tag_repo
from app.schemas.tag_schema import TagCreate, TagUpdate
from app.security.models.log_model import ActionType, EntityType
from app.security.models.user_model import User
from app.security.services import log_service
from app.services import client_service


def _register_tag_log(
    db: Session,
    user_id: int,
    action: ActionType,
    tag_id: int,
) -> None:
    log_service.register_log(
        db=db,
        user_id=user_id,
        action=action,
        affected_entity=EntityType.TAG,
        affected_entity_id=tag_id,
    )


def _save_tag_with_log(
    db: Session,
    tag: Tag,
    user_id: int,
    action: ActionType,
) -> Tag:
    try:
        tag_repo.save(db, tag)
        _register_tag_log(db, user_id, action, tag.id)
        db.commit()
        db.refresh(tag)
        return tag
    except IntegrityError as exc:
        db.rollback()
        # MySQL error 1062 identifies a unique constraint violation.
        if exc.orig.args and exc.orig.args[0] == 1062:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La MAC o la IP ya está asignada a otro tag.",
            ) from exc
        raise
    except Exception:
        db.rollback()
        raise


def get_tag(db: Session, tag_id: int) -> Tag:
    tag = tag_repo.find_by_id(db, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag no encontrado.",
        )
    return tag


def get_tags(db: Session, offset: int, limit: int) -> list[Tag]:
    return tag_repo.find_all(db, offset, limit)


def get_tags_by_users(
    db: Session,
    user_id: int,
    offset: int,
    limit: int,
) -> list[Tag]:
    return tag_repo.find_all_by_users(db, user_id, offset, limit)


def get_tags_by_client(
    db: Session,
    client_id: int,
    offset: int,
    limit: int,
) -> list[Tag]:
    return tag_repo.find_by_client_id(db, client_id, offset, limit)


def create_tag(
    db: Session,
    data: TagCreate,
    current_user: User,
) -> Tag:
    client = client_service.get_active_client(db, data.client_id)
    tag = Tag(
        client_id=client.id,
        device_type=data.device_type,
        brand=data.brand,
        model=data.model,
        mac=data.mac,
        ip=data.ip,
    )
    return _save_tag_with_log(db, tag, current_user.id, ActionType.CREATE)


def update_tag(
    db: Session,
    tag_id: int,
    data: TagUpdate,
    current_user: User,
) -> Tag:
    tag = get_tag(db, tag_id)
    client_service.get_active_client(db, tag.client_id)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return tag

    for field, value in updates.items():
        setattr(tag, field, value)
    return _save_tag_with_log(db, tag, current_user.id, ActionType.UPDATE)


def delete_tag(db: Session, tag_id: int, current_user: User) -> None:
    tag = get_tag(db, tag_id)
    try:
        tag_repo.delete(db, tag)
        _register_tag_log(db, current_user.id, ActionType.DELETE, tag.id)
        db.commit()
    except Exception:
        db.rollback()
        raise
