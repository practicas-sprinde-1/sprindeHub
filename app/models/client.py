from typing import TYPE_CHECKING, ClassVar

from sqlalchemy import String, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user_favorite_client_model import UserFavoriteClient
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
        back_populates="client",
        passive_deletes=True,
    )

    user_clients: Mapped[list["UserClient"]] = relationship(
        back_populates="client",
        passive_deletes=True,
    )

    user_favorites: Mapped[list["UserFavoriteClient"]] = relationship(
        back_populates="client",
        # cascade="all, delete-orphan": El hijo le pertenece solo a este padre. Si se desvincula o el padre muere, el hijo se borra de la BD.
        # passive_deletes=True: Delega el borrado a la BD  para no cargar los hijos en memoria. Requiere el ondelete="CASCADE" en la tabla hija.
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
