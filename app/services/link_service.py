from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.link import Link
from app.repositories import link_repo
from app.schemas.link_schema import LinkCreate,LinkUpdate
from app.services import project_service

def get_link(
        db:Session,
        link_id:int
)-> Link:
    link = link_repo.find_by_id(db,link_id)
    if link is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Link no encontrado"
        )
    return link

def get_link_by_id_project(
        db:Session,
        project_id:int,
        offset:int,
        limit:int

)-> list[Link]:
    links = link_repo.find_by_project_id(db,project_id,offset,limit)
    return links

def get_links(
        db:Session,
        offset:int,
        limit:int
)->list[Link]:
    return link_repo.find_all(db,offset,limit)

def create_link(
        db:Session,
        data:LinkCreate
)->Link:


    project = project_service.get_active_project(db,data.project_id)

    link = Link(
        url=data.url,
        project_id=project.id,
        title=data.title
    )
    return link_repo.save(db,link)

def update_link(
        db:Session,
        link_id:int,
        data:LinkUpdate
)->Link:
    link = get_link(db,link_id)

    updates = data.model_dump(
        exclude_unset=True
    )
    if "project_id" in updates:
        project_service.get_active_project(db,updates["project_id"])

    for field,value in updates.items():
        setattr(link,field,value)

    return link_repo.save(db,link)

def delete_link(
        db:Session,
        link_id:int
)->str:
    link = get_link(db,link_id)
    name_project = link.project.name

    link_repo.delete(db,link)
    return f"El link del proyecto {name_project} ha sido borrado correctamente"


