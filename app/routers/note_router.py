from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.note import Note
from app.models.project import Project
from app.schemas.note_schema import NoteCreate, NoteRead, NoteUpdate
from app.security.dependencies import (
    get_active_current_user,
    require_modifier_role,
    require_project_access,
)
from app.security.models.user_model import RoleType, User
from app.services import note_service

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
)

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_active_current_user)]
CurrentWriter = Annotated[User, Depends(require_modifier_role)]
AccessibleProject = Annotated[Project, Depends(require_project_access)]


def _get_accessible_note(
    db: Session,
    note_id: int,
    current_user: User,
) -> Note:
    note = note_service.get_note(db, note_id)
    require_project_access(note.project_id, db, current_user)
    return note

def _validate_optional_project_access(
    db: Session,
    project_id: int | None,
    current_user: User,
) -> None:
    if project_id is None:
        return

    require_project_access(project_id, db, current_user)

@router.get(
    "",
    response_model=list[NoteRead],
)
def find_all(
    db: DbSession,
    current_user: CurrentUser,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    if current_user.role == RoleType.ADMIN:
        return note_service.get_notes(db, offset, limit)

    return note_service.get_notes_by_users(db, current_user.id, offset, limit)


@router.get(
    "/{note_id}",
    response_model=NoteRead,
)
def find_by_id(
    db: DbSession,
    note_id: int,
    current_user: CurrentUser,
):
    return _get_accessible_note(db, note_id, current_user)


@router.get(
    "/project/{project_id}",
    response_model=list[NoteRead],
)
def find_by_project_id(
    db: DbSession,
    project: AccessibleProject,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return note_service.get_notes_by_id_project(db, project.id, offset, limit)


@router.post(
    "",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
)
def create(
    db: DbSession,
    data: NoteCreate,
    current_user: CurrentWriter,
):
    require_project_access(data.project_id, db, current_user)
    return note_service.create_note(db, data, current_user)


@router.patch(
    "/{note_id}",
    response_model=NoteRead,
)
def update(
    db: DbSession,
    note_id: int,
    data: NoteUpdate,
    current_user: CurrentWriter,
):
    _get_accessible_note(db, note_id, current_user)

    _validate_optional_project_access(db,data.project_id,current_user)

    return note_service.update_note(db, note_id, data, current_user)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    db: DbSession,
    note_id: int,
    current_user: CurrentWriter,
) -> None:
    _get_accessible_note(db, note_id, current_user)
    note_service.delete_note(db, note_id, current_user)
