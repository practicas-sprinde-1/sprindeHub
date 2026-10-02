from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.security.models.user_model import User
from app.security.repositories import user_repo
from app.security.schemas.user_token_schemas import UserRegister, UserLogin, Token
from app.security.utils import hash_password, verify_password, create_access_token
from app.services import client_service


def get_user(
        db:Session,
        user_id:int
)-> User:
    user = user_repo.find_by_id(db,user_id)
    if user is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Usuario no encontrado"
        )
    return user

def get_users_by_id_client(
        db:Session,
        client_id:int,
        offset:int,
        limit:int

)-> list[User]:

    client_service.get_client(db,client_id)
    users = user_repo.find_by_client_id(db,client_id,offset,limit)
    return users

def get_users(
        db:Session,
        offset:int,
        limit:int
)->list[User]:
    return user_repo.find_all(db,offset,limit)


def get_inactive_users(
        db:Session,
        offset:int,
        limit:int
)->list[User]:
    return user_repo.find_all_inactive(db,offset,limit)


def create_user(
        db:Session,
        data:UserRegister
)->User:

    if user_repo.find_by_email(db,str(data.email)):
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail= "Email ya registrado."
        )
    if user_repo.find_by_username(db,data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username ya registrado"
        )
    crypted_password = hash_password(data.password)
    user = User(
        email=data.email,
        username=data.username,
        password_hash=crypted_password
    )
    return user_repo.save(db,user)

def login_user(
        db:Session,
        data:UserLogin
)->Token:
    user = user_repo.find_by_email(db,str(data.email))

    if user is None or not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta está desactivada"
        )

    access_token = create_access_token(user.id)

    return Token(access_token=access_token)




def restore_user(
        db:Session,
        user_id:int
)->User:
    user = get_user(db,user_id)

    user.is_active=True

    return user_repo.save(db,user)


def inactive_user(
        db: Session,
        user_id: int
) -> User:
    user = get_user(db, user_id)

    user.is_active = False

    return user_repo.save(db, user)

def get_active_user(
        db:Session,
        user_id:int
)->User:
    user = get_user(db,user_id)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está inactivo",
        )
    return user