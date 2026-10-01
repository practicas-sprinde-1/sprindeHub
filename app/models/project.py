from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Text, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.environment import Environment
    from app.models.repository import Repository
    from app.models.link import Link
    from app.models.service import Service
    from app.models.command import Command
    from app.models.domain import Domain


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        unique=True
    )

    description: Mapped[str|None] = mapped_column(
        Text,
        nullable=True,
    )

    client: Mapped["Client"] = relationship(
        back_populates="projects"
    )

    environments: Mapped[list["Environment"]] = relationship(
        back_populates="project"
    )

    repositories: Mapped[list["Repository"]] = relationship(
        back_populates="project"
    )

    domains: Mapped[list["Domain"]] = relationship(
        back_populates="project"
    )

    links: Mapped[list["Link"]] = relationship(
        back_populates="project"
    )

    services: Mapped[list["Service"]] = relationship(
        back_populates="project"
    )

    commands: Mapped[list["Command"]] = relationship(
        back_populates="project"
    )


    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
    )

