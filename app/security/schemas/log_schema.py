from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.security.models.log_model import EntityType, ActionType


class LogRead(BaseModel):
    id:int
    user_id:int
    action:ActionType
    affected_entity:EntityType
    affected_entity_id:int
    created_at:datetime
    model_config = ConfigDict(from_attributes=True)


