from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey,Text
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.project import Project

class  Note(Base):
    __tablename__ = "notes"

    id:Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
       Text,
        nullable=False,
    )


    project: Mapped["Project"] = relationship(
        back_populates="notes",
    )






