from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base
from app.models.client import Client
from app.security.models.user_model import User


class UserFavoriteClient(Base):
    __tablename__ = "user_favorite_clients"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship(back_populates="favorite_clients")
    client: Mapped["Client"] = relationship(back_populates="user_favorites")
