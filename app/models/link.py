from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.project import Project


class  Link(Base):
    __tablename__ = "links"

    id:Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    title:Mapped[str]= mapped_column(
        String(255),
        nullable=False
    )


    url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    project: Mapped["Project"] = relationship(
        back_populates="links",
    )






