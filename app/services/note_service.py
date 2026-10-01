from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.note import Note
from app.repositories import note_repo
from app.schemas.note_schema import NoteCreate,NoteUpdate
from app.services import project_service

def get_note(
        db:Session,
        note_id:int
)-> Note:
    note = note_repo.find_by_id(db,note_id)
    if note is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Nota no encontrado"
        )
    return note

def get_notes_by_id_project(
        db:Session,
        project_id:int,
        offset:int,
        limit:int

)-> list[Note]:
    notes = note_repo.find_by_project_id(db,project_id,offset,limit)
    return notes

def get_notes(
        db:Session,
        offset:int,
        limit:int
)->list[Note]:
    return note_repo.find_all(db,offset,limit)

def create_note(
        db:Session,
        data:NoteCreate
)->Note:


    project = project_service.get_active_project(db,data.project_id)

    note = Note(
        description=data.description,
        project_id=project.id,
        content=data.content
    )
    return note_repo.save(db,note)

def update_note(
        db:Session,
        note_id:int,
        data:NoteUpdate
)->Note:
    note = get_note(db,note_id)

    updates = data.model_dump(
        exclude_unset=True
    )
    if "project_id" in updates:
        project_service.get_active_project(db,updates["project_id"])

    for field,value in updates.items():
        setattr(note,field,value)

    return note_repo.save(db,note)

def delete_note(
        db:Session,
        note_id:int
)->str:
    note = get_note(db,note_id)
    description_project = note.project.description

    note_repo.delete(db,note)
    return f"La nota del proyecto {description_project} ha sido borrada correctamente"


