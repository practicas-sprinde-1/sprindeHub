from typing import TYPE_CHECKING

from enum import Enum

from sqlalchemy import Enum as SqlEnum, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.project import Project

class RepositoryType(str, Enum):
    BACKEND = "backend"
    FRONTEND= "frontend"
    DEVOPS = "devops"
    QA ="qa"

class  Repository(Base):
    __tablename__ = "repositories"

    id:Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    type: Mapped[RepositoryType] = mapped_column(

        SqlEnum(RepositoryType, name="repository_type"),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    project: Mapped["Project"] = relationship(
        back_populates="repositories",
    )






