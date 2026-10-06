from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.environment import Environment
from app.repositories import environment_repo
from app.schemas.environment_schema import EnvironmentCreate,EnvironmentUpdate
from app.security.models.log_model import ActionType, EntityType
from app.security.models.user_model import User
from app.security.services import log_service
from app.services import project_service

def get_environment(
        db:Session,
        environment_id:int
)-> Environment:
    environment = environment_repo.find_by_id(db,environment_id)
    if environment is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Entorno no encontrado"
        )
    return environment

def get_environment_by_id_project(
        db:Session,
        project_id:int,
        offset:int,
        limit:int

)-> list[Environment]:
    environments = environment_repo.find_by_project_id(db,project_id,offset,limit)
    return environments

def get_environments(
        db:Session,
        offset:int,
        limit:int
)->list[Environment]:
    return environment_repo.find_all(db,offset,limit)

def get_environments_by_users(
        db:Session,
        user_id:int,
        offset:int,
        limit:int
)->list[Environment]:
    return environment_repo.find_all_by_users(db,user_id,offset,limit)


def create_environment(
        db:Session,
        data:EnvironmentCreate,
        current_user:User
)->Environment:


    project = project_service.get_active_project(db,data.project_id)

    environment = Environment(
        type=data.type,
        url=data.url,
        project_id=project.id
    )

    try:
        environment_repo.save(db, environment)

        log_service.register_log(
            db=db,
            user_id=current_user.id,
            action=ActionType.CREATE,
            affected_entity=EntityType.ENVIRONMENT,
            affected_entity_id=environment.id
        )
        db.commit()
        db.refresh(environment)
        return environment

    except Exception:
        db.rollback()
        raise





def update_environment(
        db:Session,
        environment_id:int,
        data:EnvironmentUpdate,
        current_user:User
)->Environment:
    environment = get_environment(db,environment_id)

    updates = data.model_dump(
        exclude_unset=True
    )
    if "project_id" in updates:
        project_service.get_active_project(db,updates["project_id"])

    for field,value in updates.items():
        setattr(environment,field,value)

    try:
        environment_repo.save(db, environment)
        log_service.register_log(
            db=db,
            user_id=current_user.id,
            action=ActionType.UPDATE,
            affected_entity=EntityType.ENVIRONMENT,
            affected_entity_id=environment.id
        )
        db.commit()
        db.refresh(environment)
        return environment

    except Exception:
        db.rollback()
        raise





def delete_environment(
        db:Session,
        environment_id:int,
        current_user:User
)->str:
    environment = get_environment(db,environment_id)
    name_project = environment.project.name

    try:
        environment_repo.delete(db, environment)

        log_service.register_log(
            db=db,
            user_id=current_user.id,
            action=ActionType.DELETE,
            affected_entity=EntityType.ENVIRONMENT,
            affected_entity_id=environment.id
        )
        db.commit()
        return f"El entorno del proyecto {name_project} ha sido borrado correctamente"

    except Exception:
        db.rollback()
        raise



