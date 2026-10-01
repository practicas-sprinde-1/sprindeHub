from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.environment import Environment
from app.repositories import environment_repo
from app.schemas.environment_schema import EnvironmentCreate,EnvironmentUpdate
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

def create_environment(
        db:Session,
        data:EnvironmentCreate
)->Environment:


    project = project_service.get_active_project(db,data.project_id)

    environment = Environment(
        type=data.type,
        url=data.url,
        project_id=project.id
    )
    return environment_repo.save(db,environment)

def update_environment(
        db:Session,
        environment_id:int,
        data:EnvironmentUpdate
)->Environment:
    environment = get_environment(db,environment_id)

    updates = data.model_dump(
        exclude_unset=True
    )
    if "project_id" in updates:
        project_service.get_active_project(db,updates["project_id"])

    for field,value in updates.items():
        setattr(environment,field,value)

    return environment_repo.save(db,environment)

def delete_environment(
        db:Session,
        environment_id:int
)->str:
    environment = get_environment(db,environment_id)
    name_project = environment.project.name

    environment_repo.delete(db,environment)
    return f"El entorno del proyecto {name_project} ha sido borrado correctamente"


