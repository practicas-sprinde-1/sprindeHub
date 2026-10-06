from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.domain import Domain
from app.repositories import domain_repo
from app.schemas.domain_schema import DomainCreate,DomainUpdate
from app.services import project_service

def get_domain(
        db:Session,
        domain_id:int
)-> Domain:
    domain = domain_repo.find_by_id(db,domain_id)
    if domain is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Dominio no encontrado"
        )
    return domain

def get_domain_by_id_project(
        db:Session,
        project_id:int,
        offset:int,
        limit:int

)-> list[Domain]:
    domains = domain_repo.find_by_project_id(db,project_id,offset,limit)
    return domains

def get_domains(
        db:Session,
        offset:int,
        limit:int
)->list[Domain]:
    return domain_repo.find_all(db,offset,limit)

def get_domains_by_users(
        db:Session,
        user_id:int,
        offset:int,
        limit:int
)->list[Domain]:
    return domain_repo.find_all_by_users(db,user_id,offset,limit)

def create_domain(
        db:Session,
        data:DomainCreate
)->Domain:


    project = project_service.get_active_project(db,data.project_id)

    domain = Domain(
        url=data.url,
        project_id=project.id
    )
    return domain_repo.save(db,domain)

def update_domain(
        db:Session,
        domain_id:int,
        data:DomainUpdate
)->Domain:
    domain = get_domain(db,domain_id)

    updates = data.model_dump(
        exclude_unset=True
    )
    if "project_id" in updates:
        project_service.get_active_project(db,updates["project_id"])

    for field,value in updates.items():
        setattr(domain,field,value)

    return domain_repo.save(db,domain)

def delete_domain(
        db:Session,
        domain_id:int
)->str:
    domain = get_domain(db,domain_id)
    name_project = domain.project.name

    domain_repo.delete(db,domain)
    return f"El dominio del proyecto {name_project} ha sido borrado correctamente"


