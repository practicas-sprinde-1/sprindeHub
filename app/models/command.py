from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.project import Project

class  Command(Base):
    __tablename__ = "commands"

    id:Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    instruction: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    project: Mapped["Project"] = relationship(
        back_populates="commands",
    )






