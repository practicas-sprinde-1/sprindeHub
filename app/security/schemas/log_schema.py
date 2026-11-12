from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from app.security.models.log_model import EntityType, ActionType


def _parse_log_date(date_text: str) -> date:
    parsed_date = date.fromisoformat(date_text)
    formatted_date = parsed_date.isoformat()
    if date_text != formatted_date:
        raise ValueError("La fecha debe tener el formato YYYY-MM-DD.")

    return parsed_date


LogDate = Annotated[date, BeforeValidator(_parse_log_date)]


class LogRead(BaseModel):
    id: int
    user_id: int
    action: ActionType
    affected_entity: EntityType
    affected_entity_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LogPage(BaseModel):
    items: list[LogRead]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)
