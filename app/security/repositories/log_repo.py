from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.security.models.log_model import ActionType, EntityType, Log
from app.security.models.user_model import User
from app.security.schemas.log_schema import LogPage, LogRead


def _filter_by_search_and_username(
        statement: Select,
        search: str | None,
        username: str | None = None,
) -> Select:
    search_term = ""
    if search is not None:
        search_term = search.strip()

    has_search = search_term != ""
    if has_search or username is not None:
        statement = statement.join(User, User.id == Log.user_id)

    if username is not None:
        statement = statement.where(User.username == username)
    if has_search:
        pattern = f"%{search_term}%"
        username_matches_search = User.username.ilike(pattern)
        log_text_matches_search = Log.search_text.ilike(pattern)
        statement = statement.where(or_(username_matches_search, log_text_matches_search))

    return statement


def find_all_list(
        db: Session,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
) -> list[Log]:
    statement = _filter_by_search_and_username(select(Log), search)
    statement = (
        statement
        .order_by(Log.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def _apply_list_filters(
        statement: Select,
        start_date: date | None,
        end_before: date | None,
        action: ActionType | None,
        username: str | None,
        affected_entity: EntityType | None,
        search: str | None,
) -> Select:
    if start_date is not None:
        statement = statement.where(Log.created_at >= start_date)
    if end_before is not None:
        statement = statement.where(Log.created_at < end_before)
    if action is not None:
        statement = statement.where(Log.action == action)
    if affected_entity is not None:
        statement = statement.where(Log.affected_entity == affected_entity)

    return _filter_by_search_and_username(statement, search, username=username)


def _find_all(
        db: Session,
        offset: int,
        limit: int,
        start_date: date | None,
        end_before: date | None,
        action: ActionType | None,
        username: str | None,
        affected_entity: EntityType | None,
        search: str | None,
) -> LogPage:
    total_statement = select(func.count(Log.id))
    total_statement = _apply_list_filters(
        total_statement,
        start_date=start_date,
        end_before=end_before,
        action=action,
        username=username,
        affected_entity=affected_entity,
        search=search,
    )
    total = db.scalar(total_statement) or 0

    logs = []
    if offset < total:
        statement = select(Log)
        statement = _apply_list_filters(
            statement,
            start_date=start_date,
            end_before=end_before,
            action=action,
            username=username,
            affected_entity=affected_entity,
            search=search,
        )
        statement = statement.order_by(Log.created_at.desc(), Log.id.desc())
        statement = statement.offset(offset)
        statement = statement.limit(limit)
        logs = list(db.scalars(statement).all())

    items = []
    for log in logs:
        item = LogRead.model_validate(log)
        items.append(item)

    return LogPage(items=items, total=total, offset=offset, limit=limit)


def find_all(
        db: Session,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
        start_date: date | None = None,
        end_before: date | None = None,
        action: ActionType | None = None,
        username: str | None = None,
        affected_entity: EntityType | None = None,
) -> LogPage:
    return _find_all(
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


def find_all_by_users(
        db: Session,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
) -> list[Log]:
    statement = (
        select(Log)
        .where(Log.user_id == user_id)
        .order_by(Log.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def find_all_by_entity(
        db: Session,
        entity_id: int,
        affected_entity: EntityType,
        offset: int = 0,
        limit: int = 20,
) -> list[Log]:
    statement = (
        select(Log)
        .where(Log.affected_entity_id == entity_id, Log.affected_entity == affected_entity)
        .order_by(Log.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def find_by_id(
        db: Session,
        log_id: int,
) -> Log | None:
    return db.get(Log, log_id)


def save(
        db: Session,
        log: Log,
) -> Log:
    db.add(log)
    db.flush()
    return log
