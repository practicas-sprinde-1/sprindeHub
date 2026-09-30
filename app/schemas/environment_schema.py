from pydantic import BaseModel, Field, ConfigDict

from app.models.environment import EnvironmentType


class EnvironmentBase(BaseModel):
    type: EnvironmentType
    url:str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^https?://"
    )
    project_id:int = Field(gt=0)

class EnvironmentCreate(EnvironmentBase):
    pass

class EnvironmentUpdate(BaseModel):
    type: EnvironmentType | None=Field(
        default=None
    )
    url:str|None = Field(
        default=None,
        min_length=1,
        max_length=255,
        pattern=r"^https?://"
    )
    project_id:int|None=Field(
        default=None,
        gt=0
    )

class EnvironmentRead(EnvironmentBase):
    id:int
    model_config=ConfigDict(from_attributes=True)



