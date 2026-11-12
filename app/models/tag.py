from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.client import Client


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey(
            "clients.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    device_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    brand: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    mac: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )
    ip: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )

    client: Mapped["Client"] = relationship(
        back_populates="tags",
    )
