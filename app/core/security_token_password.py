from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

from app.core.config import settings

# Encriptador de password
password_hasher = PasswordHash.recommended()

# Recibe una password en texto plano y devuelve la password encriptada
def hash_password(password: str) -> str:
    return password_hasher.hash(password)

# Comprueba que la contraseña que se recibe por parámetro sea igual que la encriptada en la BBDD
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)

# Crea un token de acceso recibiendo por parametro el user_id
def create_access_token(user_id: int) -> str:
    #Calcula el expires sumando la hora que se registra con el tiempo que he configurado en .ENV
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=settings.access_token_minutes)

    # Encapsula los datos del token. Quién(subject),cuándo se creó(issuedAt) y cuándo expira(Expired).
    token_data = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires,
    }

    #Se fabrica el jwt firmándolo con la password de .env y usando tambien el algoritmo definido en .env
    return jwt.encode(
        token_data,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

#Recibe un token y comprueba si es válido
def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )