from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.schemas.note_schema import NoteRead,NoteCreate,NoteUpdate
from app.services import note_service

router = APIRouter(
    prefix="/notes",
    tags=["notes"]
)

DbSession = Annotated[
    Session,
    Depends(get_db)
]

@router.get(
    "",
    response_model=list[NoteRead]
)
def find_all(
        db:DbSession,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return note_service.get_notes(db,offset,limit)

@router.get(
    "/{note_id}",
    response_model=NoteRead
)
def find_by_id(
        db:DbSession,
        note_id:int
):
    return note_service.get_note(db,note_id)

@router.get(
    "/project/{project_id}",
    response_model=list[NoteRead]
)
def find_by_project_id(
        db:DbSession,
        project_id:int,
        offset:int = Query(default=0,ge=0),
        limit:int=Query(default=20,ge=1,le=100)
):
    return note_service.get_notes_by_id_project(db,project_id,offset,limit)

@router.post(
    "",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED
)
def create(
        db: DbSession,
        data: NoteCreate
):
    return note_service.create_note(db, data)


@router.patch(
    "/{note_id}",
    response_model=NoteRead
)
def update(
        db: DbSession,
        note_id: int,
        data: NoteUpdate
):
    return note_service.update_note(db, note_id, data)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete(
        db: DbSession,
        note_id: int
) -> None:
    note_service.delete_note(db, note_id)

