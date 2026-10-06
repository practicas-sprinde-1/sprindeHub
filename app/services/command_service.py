from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.command import Command
from app.repositories import command_repo
from app.schemas.command_schema import CommandCreate,CommandUpdate
from app.services import project_service

def get_command(
        db:Session,
        command_id:int
)-> Command:
    command = command_repo.find_by_id(db,command_id)
    if command is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Comando no encontrado"
        )
    return command

def get_commands_by_id_project(
        db:Session,
        project_id:int,
        offset:int,
        limit:int

)-> list[Command]:
    commands = command_repo.find_by_project_id(db,project_id,offset,limit)
    return commands

def get_commands(
        db:Session,
        offset:int,
        limit:int
)->list[Command]:
    return command_repo.find_all(db,offset,limit)

def get_commands_by_users(
        db:Session,
        user_id:int,
        offset:int,
        limit:int
)->list[Command]:
    return command_repo.find_all_by_users(db,user_id,offset,limit)

def create_command(
        db:Session,
        data:CommandCreate
)->Command:


    project = project_service.get_active_project(db,data.project_id)

    command = Command(
        name=data.name,
        project_id=project.id,
        instruction=data.instruction
    )
    return command_repo.save(db,command)

def update_command(
        db:Session,
        command_id:int,
        data:CommandUpdate
)->Command:
    command = get_command(db,command_id)

    updates = data.model_dump(
        exclude_unset=True
    )
    if "project_id" in updates:
        project_service.get_active_project(db,updates["project_id"])

    for field,value in updates.items():
        setattr(command,field,value)

    return command_repo.save(db,command)

def delete_command(
        db:Session,
        command_id:int
)->str:
    command = get_command(db,command_id)
    name_project = command.project.name

    command_repo.delete(db,command)
    return f"El comando del proyecto {name_project} ha sido borrado correctamente"


