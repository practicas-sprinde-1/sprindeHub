from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SqlEnum, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.security.models.user_client_model import UserClient
    from app.models.user_favorite_client_model import UserFavoriteClient
    from app.models.user_favorite_project_model import UserFavoriteProject


# Elimina la etiqueta de la zona horaria con usando el .replace
def utc_now_db() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class RoleType(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST = "GUEST"


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

    role: Mapped[RoleType] = mapped_column(
        SqlEnum(RoleType, name="role_type"),
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

    user_clients: Mapped[list["UserClient"]] = relationship(back_populates="user")

    favorite_clients: Mapped[list["UserFavoriteClient"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    favorite_projects: Mapped[list["UserFavoriteProject"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
