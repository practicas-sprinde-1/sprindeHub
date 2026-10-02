import enum
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Enum as SqlEnum ,BigInteger, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base_class import Base

#Elimina la etiqueta de la zona horaria con usando el .replace
def utc_now_db() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class RoleType(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST ="GUEST"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    email: Mapped[str] = mapped_column(
        String(254),
        unique=True,
        nullable=False
    )

    username: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="GUEST",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now_db,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now_db,
        onupdate=utc_now_db,
        nullable=False,
    )