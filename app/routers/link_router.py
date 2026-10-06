from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.project import Project
from app.schemas.link_schema import LinkRead,LinkCreate,LinkUpdate
from app.security.dependencies import get_active_current_user, require_modifier_role, require_project_access
from app.security.models.user_model import User, RoleType
from app.services import link_service

router = APIRouter(
    prefix="/links",
    tags=["links"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]

CurrentUser = Annotated[
    User, Depends(get_active_current_user)
]

CurrentWriter = Annotated[
    User,Depends(require_modifier_role)
]

CurrentProject = Annotated[
    Project,Depends(require_project_access)
]

@router.get(
    "",
    response_model=list[LinkRead]
)
def find_all(
        db:DbSession,
        current_user:CurrentUser,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    if current_user.role == RoleType.ADMIN:
        return link_service.get_links(db,offset,limit)
    return link_service.get_links_by_users(db,current_user.id,offset, limit)

@router.get(
    "/{link_id}",
    response_model=LinkRead
)
def find_by_id(
        db:DbSession,
        link_id:int,
        current_user:CurrentUser
):
    link = link_service.get_link(db,link_id)
    require_project_access(link.project_id,db,current_user)
    return link

@router.get(
    "/project/{project_id}",
    response_model=list[LinkRead]
)
def find_by_project_id(
        db:DbSession,
        current_project:CurrentProject,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return link_service.get_link_by_id_project(db,current_project.id,offset,limit)

@router.post(
    "",
    response_model=LinkRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: LinkCreate,
        current_user:CurrentWriter
):
    require_project_access(data.project_id,db,current_user)
    return link_service.create_link(db, data)


@router.patch(
    "/{link_id}",
    response_model=LinkRead
)
def update(
        db: DbSession,
        link_id: int,
        data: LinkUpdate,
        current_user:CurrentWriter
):
    link = link_service.get_link(db,link_id)
    require_project_access(link.project_id,db,current_user)

    if data.project_id is not None:
        require_project_access(data.project_id,db,current_user)
    return link_service.update_link(db, link_id, data)


@router.delete(
    "/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        link_id: int,
        current_user:CurrentWriter
) -> None:
    link = link_service.get_link(db,link_id)
    require_project_access(link.project_id,db,current_user)
    link_service.delete_link(db, link_id)

