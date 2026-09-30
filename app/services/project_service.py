from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories import project_repo
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from app.services import client_service


def get_project(
        db:Session,
        project_id:int
)-> Project:
    project = project_repo.find_by_id(db,project_id)
    if project is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Proyecto no encontrado"
        )
    return project

def get_projects_by_id_client(
        db:Session,
        client_id:int,
        offset:int,
        limit:int

)-> list[Project]:
    projects = project_repo.find_by_client_id(db,client_id,offset,limit)
    return projects

def get_projects(
        db:Session,
        offset:int,
        limit:int
)->list[Project]:
    return project_repo.find_all(db,offset,limit)


def create_project(
        db:Session,
        data:ProjectCreate
)->Project:
    client = client_service.get_active_client(db,data.client_id)



    project = Project(
        name=data.name,
        description=data.description,
        client_id=client.id
    )
    return project_repo.save(db,project)



def update_project(
        db:Session,
        project_id:int,
        data: ProjectUpdate
)->Project:
    project = get_project(db,project_id)

    updates = data.model_dump(
        exclude_unset=True
    )
    if "client_id" in updates:
        client_service.get_active_client(db,updates["client_id"])

    for field,value in updates.items():
        setattr(project,field,value)

    return project_repo.save(db,project)



def delete_project(
        db:Session,
        project_id:int
)->str:
    project = get_project(db,project_id)

    project_name = project.name
    client_name = project.client.name

    project_repo.delete(db,project)
    return f"El proyecto{project_name} del cliente {client_name} ha sido borrado correctamente"