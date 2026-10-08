import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.security.models.user_model import User
from app.security.repositories import user_repo
from app.security.schemas.user_token_schemas import UserRegister, UserLogin, Token, UserSelfUpdate, PasswordChange, \
    AdminUserCreate, AdminUserUpdate, RefreshTokenRequest, AccessToken
from app.security.utils import hash_password, verify_password, create_access_token, create_refresh_token, \
    decode_access_token
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
        email=str(data.email),
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
    refresh_token = create_refresh_token(user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )

def refresh_user(
        db:Session,
        data:RefreshTokenRequest
)->AccessToken:
    try:
        token_data = decode_access_token(data.refresh_token)

        if token_data["token_type"] != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error al refrescar, inicie sesión de nuevo."
            )
        user_id = int(token_data["sub"])

    #Captura errores que no son especificos de token
    except HTTPException:
        raise

    except (
        jwt.PyJWTError,
        KeyError,
        TypeError,
        ValueError,
        ):
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado.",
        )

    user = get_user(db,user_id)

    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este usuario está desactivado."
        )

    access_token = create_access_token(user_id)

    return AccessToken(
        access_token=access_token
    )


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

def aux_check_data(
        db:Session,
        data: AdminUserUpdate | UserSelfUpdate,
        user:User

)->dict:
    updates = data.model_dump(
        exclude_unset=True,
        exclude_none=True
    )
    if "email" in updates and updates["email"] != user.email:
        existing_user = user_repo.find_by_email(
            db,
            str(updates["email"]),
        )
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email ya registrado.",
            )
    if "username" in updates and updates["username"] != user.username:
        existing_user = user_repo.find_by_username(
            db,
            updates["username"],
        )
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username ya registrado.",
            )
    return updates

def update_self_user(
        db:Session,
        user_id:int,
        data:UserSelfUpdate
)->User:
    user = get_user(db, user_id)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está inactivo",
        )
    updates = aux_check_data(db,data,user)
    for field,value in updates.items():
        setattr(user,field,value)

    return user_repo.save(db,user)

def change_password(
        db:Session,
        user_id:int,
        data: PasswordChange
)->str:
    user = get_user(db, user_id)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está inactivo",
        )

    if not verify_password(
            data.current_password,
            user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Las contraseñas no coinciden",
        )
    new_password = data.new_password
    encrypted_new_pass = hash_password(new_password)

    user.password_hash = encrypted_new_pass

    user_repo.save(db,user)
    return "Contraseña cambiada"

def admin_create_user(
        db:Session,
        data:AdminUserCreate
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
        email=str(data.email),
        username=data.username,
        password_hash=crypted_password,
        role=data.role,
        is_active=data.is_active,
    )
    return user_repo.save(db, user)


def admin_update_user(
        db: Session,
        user_id: int,
        data: AdminUserUpdate
) -> User:

    user = get_user(db, user_id)
    updates = aux_check_data(db,data,user)

    for field, value in updates.items():
        setattr(user, field, value)

    return user_repo.save(db, user)



