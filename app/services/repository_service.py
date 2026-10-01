from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.repository import Repository
from app.repositories import repository_repo
from app.schemas.repository_schema import RepositoryCreate,RepositoryUpdate
from app.services import project_service

def get_repository(
        db:Session,
        repository_id:int
)-> Repository:
    repository = repository_repo.find_by_id(db,repository_id)
    if repository is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Repositorio no encontrado"
        )
    return repository

def get_repository_by_id_project(
        db:Session,
        project_id:int,
        offset:int,
        limit:int

)-> list[Repository]:
    repositories = repository_repo.find_by_project_id(db,project_id,offset,limit)
    return repositories

def get_repositories(
        db:Session,
        offset:int,
        limit:int
)->list[Repository]:
    return repository_repo.find_all(db,offset,limit)

def create_repository(
        db:Session,
        data:RepositoryCreate
)->Repository:


    project = project_service.get_active_project(db,data.project_id)

    repository = Repository(
        type=data.type,
        url=data.url,
        project_id=project.id
    )
    return repository_repo.save(db,repository)

def update_repository(
        db:Session,
        repository_id:int,
        data:RepositoryUpdate
)->Repository:
    repository = get_repository(db,repository_id)

    updates = data.model_dump(
        exclude_unset=True
    )
    if "project_id" in updates:
        project_service.get_active_project(db,updates["project_id"])

    for field,value in updates.items():
        setattr(repository,field,value)

    return repository_repo.save(db,repository)

def delete_repository(
        db:Session,
        repository_id:int
)->str:
    repository = get_repository(db,repository_id)
    name_project = repository.project.name

    repository_repo.delete(db,repository)
    return f"El repositorio del proyecto {name_project} ha sido borrado correctamente"


