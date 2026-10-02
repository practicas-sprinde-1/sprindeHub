from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Enum as SqlEnum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base_class import Base

def utc_now_db() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class ActionType(str, Enum):
    CREATE = "CREATE"
    UPDATE ="UPDATE"
    DELETE = "DELETE"

class EntityType(str,Enum):
    CLIENT = "CLIENT"
    COMMAND ="COMMAND"
    DOMAIN ="DOMAIN"
    ENVIRONMENT="ENVIRONMENT"
    LINK="LINK"
    NOTE="NOTE"
    PROJECT="PROJECT"
    REPOSITORY="REPOSITORY"
    SERVICE="SERVICE"

class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int]=mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    action:Mapped[ActionType]=mapped_column(
        SqlEnum(ActionType, name="action_type"),
        nullable=False
    )
    affected_entity:Mapped[EntityType]=mapped_column(
        SqlEnum(EntityType, name="entity_type"),
        nullable=False
    )
    affected_entity_id: Mapped[int] = mapped_column(
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now_db,
        nullable=False,
    )


