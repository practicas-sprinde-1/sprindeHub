from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base
from app.models.client import Client

from app.security.models.user_model import User


class UserClient(Base):
    __tablename__ = "user_clients"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True,
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="user_clients",
    )

    client: Mapped["Client"] = relationship(
        back_populates="user_clients",
    )