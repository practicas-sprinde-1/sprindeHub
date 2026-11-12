from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.environment import Environment
from app.repositories import environment_repo
from app.schemas.environment_schema import EnvironmentCreate, EnvironmentUpdate
from app.security.models.log_model import ActionType, EntityType
from app.security.models.user_model import User
from app.security.services import log_service
from app.services import project_service


def _register_environment_log(
        db: Session,
        user_id: int,
        action: ActionType,
        environment_id: int,
) -> None:
    log_service.register_log(
        db=db,
        user_id=user_id,
        action=action,
        affected_entity=EntityType.ENVIRONMENT,
        affected_entity_id=environment_id,
    )


def _commit_and_refresh_environment(
        db: Session,
        environment: Environment,
) -> Environment:
    try:
        db.commit()
        db.refresh(environment)
        return environment
    except Exception:
        db.rollback()
        raise


def get_environment(
        db: Session,
        environment_id: int
) -> Environment:
    environment = environment_repo.find_by_id(db, environment_id)
    if environment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entorno no encontrado"
        )
    return environment


def get_environment_by_id_project(
        db: Session,
        project_id: int,
        offset: int,
        limit: int

) -> list[Environment]:
    environments = environment_repo.find_by_project_id(db, project_id, offset, limit)
    return environments


def get_environments(
        db: Session,
        offset: int,
        limit: int
) -> list[Environment]:
    return environment_repo.find_all(db, offset, limit)


def get_environments_by_users(
        db: Session,
        user_id: int,
        offset: int,
        limit: int
) -> list[Environment]:
    return environment_repo.find_all_by_users(db, user_id, offset, limit)


def create_environment(
        db: Session,
        data: EnvironmentCreate,
        current_user: User
) -> Environment:
    project = project_service.get_active_project(db, data.project_id)

    environment = Environment(
        type=data.type,
        url=data.url,
        project_id=project.id
    )

    try:
        environment_repo.save(db, environment)

        _register_environment_log(
            db, current_user.id, ActionType.CREATE, environment.id
        )
        return _commit_and_refresh_environment(db, environment)

    except Exception:
        db.rollback()
        raise


def update_environment(
        db: Session,
        environment_id: int,
        data: EnvironmentUpdate,
        current_user: User
) -> Environment:
    environment = get_environment(db, environment_id)

    updates = data.model_dump(
        exclude_unset=True
    )
    if "project_id" in updates:
        project_service.get_active_project(db, updates["project_id"])

    for field, value in updates.items():
        setattr(environment, field, value)

    try:
        environment_repo.save(db, environment)
        _register_environment_log(
            db, current_user.id, ActionType.UPDATE, environment.id
        )
        return _commit_and_refresh_environment(db, environment)

    except Exception:
        db.rollback()
        raise


def delete_environment(
        db: Session,
        environment_id: int,
        current_user: User
) -> str:
    environment = get_environment(db, environment_id)
    name_project = environment.project.name

    try:
        environment_repo.delete(db, environment)

        _register_environment_log(
            db, current_user.id, ActionType.DELETE, environment.id
        )
        db.commit()
        return f"El entorno del proyecto {name_project} ha sido borrado correctamente"

    except Exception:
        db.rollback()
        raise
