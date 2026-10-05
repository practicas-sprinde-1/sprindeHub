import app.database.base
from getpass import getpass

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.session import sessionLocal
from app.security.models.user_model import RoleType, User
from app.security.schemas.user_token_schemas import AdminUserCreate
from app.security.utils import hash_password


def admin_exists(db: Session) -> bool:
    statement = (
        select(User.id)
        .where(User.role == RoleType.ADMIN)
        .limit(1)
    )

    return db.scalar(statement) is not None


def create_initial_admin(
    db: Session,
    data: AdminUserCreate,
) -> User:
    if admin_exists(db):
        raise ValueError(
            "Ya existe un administrador."
        )

    email_exists = db.scalar(
        select(User.id)
        .where(User.email == data.email)
    )

    if email_exists is not None:
        raise ValueError("Ese email ya está registrado.")

    username_exists = db.scalar(
        select(User.id)
        .where(User.username == data.username)
    )

    if username_exists is not None:
        raise ValueError("Ese username ya está registrado.")

    user = User(
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password),
        role=RoleType.ADMIN,
        is_active=True,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "No se pudo crear el administrador: "
            "el email o username ya existe."
        ) from error

    return user


#Pide datos por la terminal para crear el administrador inicial
def main() -> int:

    db = sessionLocal()

    try:
        if admin_exists(db):
            print(
                "Ya existe un administrador. "
            )
            return 1

        print("Creación del administrador inicial\n")

        email = input("Email: ").strip().lower()
        username = input("Username: ").strip()

        # getpass evita mostrar la contraseña en pantalla.
        password = getpass("Contraseña: ")
        password_repeat = getpass("Repite la contraseña: ")

        if password != password_repeat:
            print("Las contraseñas no coinciden.")
            return 1

        # Reutiliza tus validaciones Pydantic:
        # EmailStr, longitud de contraseña, username, etc.
        user = AdminUserCreate.model_validate(
            {
                "email": email,
                "username": username,
                "password": password,
                "role": RoleType.ADMIN,
                "is_active": True
             }
        )

        admin = create_initial_admin(db, user)

        print(
            f"Administrador creado correctamente: "
            f"{admin.username} (id={admin.id})"
        )
        return 0

    #Captura errores específicos relacionados con Pydantic.

    except ValidationError as error:
        print("Datos inválidos:")
        print(error)
        return 1

    #Captura errores relacionadas con la app general.Ej: int("hola")

    except ValueError as error:
        print(error)
        return 1

    finally:
        db.close()

# solo se ejecuta si se llama desde consola, no desde otro modulo externo mediante importacion
#Finalmente termina el script mostrando 0 si no hubo errores o 1 si lo hubo.

if __name__ == "__main__":
    raise SystemExit(main())