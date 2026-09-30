from typing import TYPE_CHECKING

from enum import Enum

from sqlalchemy import Enum as SqlEnum, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.project import Project

#Este Enum es Python/FastAPI
class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Environment(Base):
    __tablename__ = "environments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    type: Mapped[EnvironmentType] = mapped_column(
        #Uso del alias para evitar colision de nombres.
        #Refiriendo este Enum a SQL/BDD
        SqlEnum(EnvironmentType, name="environment_type"),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    project: Mapped["Project"] = relationship(
        back_populates="environments",
    )
