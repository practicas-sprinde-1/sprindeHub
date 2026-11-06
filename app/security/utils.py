from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    issued_at = datetime.now(timezone.utc)
    #Uso de timedelta para añadir sólo los minutos a la fecha creada
    expires_at = issued_at + timedelta(minutes=settings.access_token_minutes)
    return _encode_token(
        user_id=user_id,
        issued_at=issued_at,
        expires_at=expires_at,
        token_type="access",
    )


def create_refresh_token(user_id: int) -> str:
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(days=settings.refresh_token_days)
    return _encode_token(
        user_id=user_id,
        issued_at=issued_at,
        expires_at=expires_at,
        token_type="refresh",
    )


def _encode_token(
    user_id: int,
    issued_at: datetime,
    expires_at: datetime,
    token_type: str,
) -> str:
    payload = {
        "sub": str(user_id),
        "iat": issued_at,
        "exp": expires_at,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "token_type": token_type,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )
