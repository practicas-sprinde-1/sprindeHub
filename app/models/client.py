from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.security.models.user_client_model import UserClient


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        unique=True
    )

    cif: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
        unique=True
    )

    phone: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        unique=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
    )

    projects: Mapped[list["Project"]] = relationship(
        back_populates="client"
    )

    user_clients:Mapped[list["UserClient"]] = relationship(back_populates="client")


