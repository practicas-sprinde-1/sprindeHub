from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.security.models.user_client_model import UserClient
from app.security.repositories import user_client_repo
from app.security.schemas.userClient_schema import UserClientAccess
from app.services import client_service
from app.security.services import user_service


def get_user_client(
        db:Session,
        user_id:int,
        client_id:int
)-> UserClient:
    user_client = user_client_repo.find_by_ids(db,user_id,client_id)
    if user_client is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Relacion no encontrada"
        )
    return user_client

def get_user_clients_by_client_id(
        db:Session,
        client_id:int,
        offset:int,
        limit:int

)-> list[UserClient]:

    client_service.get_client(db,client_id)
    user_clients = user_client_repo.find_by_client_id(db,client_id,offset,limit)
    return user_clients

def get_user_clients_by_user_id(
        db:Session,
        user_id:int,
        offset:int,
        limit:int

)-> list[UserClient]:

    user_service.get_user(db,user_id)
    user_clients = user_client_repo.find_by_user_id(db,user_id,offset,limit)
    return user_clients

def assign_user_to_client(
        db:Session,
        user_id:int,
        data: UserClientAccess
)->UserClient:
   user = user_service.get_user(db,user_id)
   client = client_service.get_client(db,data.client_id)

   existing_access = user_client_repo.find_by_ids(db,user.id,client.id)

   if existing_access is not None:
       raise HTTPException(
           status_code=status.HTTP_409_CONFLICT,
           detail=f"El usuario '{user.username}' ya tiene acceso al cliente '{client.name}'."
       )

   user_client = UserClient(
       user_id=user.id,
       client_id=client.id
   )

   return user_client_repo.save(db,user_client)


def revoke_client_access(
        db:Session,
        user_id:int,
        client_id:int
)->str:
   user = user_service.get_user(db,user_id)
   client = client_service.get_client(db,client_id)

   existing_access = user_client_repo.find_by_ids(db,user.id,client.id)

   if existing_access is None:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail=f"El usuario '{user.username}' no tiene acceso al cliente '{client.name}'."
       )

   user_client_repo.delete(db,existing_access)
   return f"El usuario {user.username} ya no tiene acceso al cliente {client.name}"







