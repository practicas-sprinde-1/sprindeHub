from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from app.database.base_class import Base


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
