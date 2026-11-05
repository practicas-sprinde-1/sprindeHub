from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.service import Service
from app.repositories import service_repo
from app.schemas.service_schema import ServiceCreate, ServiceUpdate
from app.security.models.log_model import ActionType, EntityType
from app.security.models.user_model import User
from app.security.services import log_service
from app.services import project_service


def _register_service_log(
        db: Session,
        user_id: int,
        action: ActionType,
        service_id: int,
) -> None:
    log_service.register_log(
        db=db,
        user_id=user_id,
        action=action,
        affected_entity=EntityType.SERVICE,
        affected_entity_id=service_id,
    )


def _commit_and_refresh_service(db: Session, service: Service) -> Service:
    try:
        db.commit()
        db.refresh(service)
        return service
    except Exception:
        db.rollback()
        raise


def get_service(
        db: Session,
        service_id: int
) -> Service:
    service = service_repo.find_by_id(db, service_id)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado"
        )
    return service


def get_service_by_id_project(
        db: Session,
        project_id: int,
        offset: int,
        limit: int

) -> list[Service]:
    services = service_repo.find_by_project_id(db, project_id, offset, limit)
    return services


def get_services(
        db: Session,
        offset: int,
        limit: int
) -> list[Service]:
    return service_repo.find_all(db, offset, limit)


def get_services_by_users(
        db: Session,
        user_id: int,
        offset: int,
        limit: int
) -> list[Service]:
    return service_repo.find_all_by_users(db, user_id, offset, limit)


def create_service(
        db: Session,
        data: ServiceCreate,
        current_user: User
) -> Service:
    project = project_service.get_active_project(db, data.project_id)

    service = Service(
        name=data.name,
        project_id=project.id,
    )
    try:
        service_repo.save(db, service)

        _register_service_log(db, current_user.id, ActionType.CREATE, service.id)
        return _commit_and_refresh_service(db, service)

    except Exception:
        db.rollback()
        raise


def update_service(
        db: Session,
        service_id: int,
        data: ServiceUpdate,
        current_user: User
) -> Service:
    service = get_service(db, service_id)

    updates = data.model_dump(
        exclude_unset=True
    )
    if "project_id" in updates:
        project_service.get_active_project(db, updates["project_id"])

    for field, value in updates.items():
        setattr(service, field, value)

    try:
        service_repo.save(db, service)

        _register_service_log(db, current_user.id, ActionType.UPDATE, service.id)
        return _commit_and_refresh_service(db, service)

    except Exception:
        db.rollback()
        raise


def delete_service(
        db: Session,
        service_id: int,
        current_user: User
) -> str:
    service = get_service(db, service_id)
    name_project = service.project.name

    try:
        service_repo.delete(db, service)

        _register_service_log(db, current_user.id, ActionType.DELETE, service.id)
        db.commit()
        return f"El servicio del proyecto {name_project} ha sido borrado correctamente"

    except Exception:
        db.rollback()
        raise
