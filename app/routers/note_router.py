from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.project import Project
from app.schemas.note_schema import NoteRead,NoteCreate,NoteUpdate
from app.security.dependencies import get_active_current_user, require_modifier_role, require_project_access
from app.security.models.user_model import User, RoleType
from app.services import note_service

router = APIRouter(
    prefix="/notes",
    tags=["notes"]
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
    response_model=list[NoteRead]
)
def find_all(
        db:DbSession,
        current_user:CurrentUser,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    if current_user.role == RoleType.ADMIN:
        return note_service.get_notes(db,offset,limit)
    return note_service.get_notes_by_users(db,current_user.id,offset, limit)

@router.get(
    "/{note_id}",
    response_model=NoteRead
)
def find_by_id(
        db:DbSession,
        note_id:int,
        current_user:CurrentUser
):
    note = note_service.get_note(db,note_id)
    require_project_access(note.project_id,db,current_user)
    return note

@router.get(
    "/project/{project_id}",
    response_model=list[NoteRead]
)
def find_by_project_id(
        db:DbSession,
        current_project:CurrentProject,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return note_service.get_notes_by_id_project(db,current_project.id,offset,limit)

@router.post(
    "",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: NoteCreate,
        current_user:CurrentWriter
):
    require_project_access(data.project_id,db,current_user)
    return note_service.create_note(db, data,current_user)


@router.patch(
    "/{note_id}",
    response_model=NoteRead
)
def update(
        db: DbSession,
        note_id: int,
        data: NoteUpdate,
        current_user:CurrentWriter
):
    note = note_service.get_note(db,note_id)
    require_project_access(note.project_id,db,current_user)

    if data.project_id is not None:
        require_project_access(data.project_id,db,current_user)
    return note_service.update_note(db, note_id, data,current_user)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        note_id: int,
        current_user:CurrentWriter
) -> None:
    note = note_service.get_note(db, note_id)
    require_project_access(note.project_id, db, current_user)
    note_service.delete_note(db, note_id,current_user)

