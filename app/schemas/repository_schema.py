from pydantic import BaseModel, Field, ConfigDict

from app.models.repository import RepositoryType


class RepositoryBase(BaseModel):
    type: RepositoryType
    url: str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^https?://"
    )
    project_id: int = Field(gt=0)

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryUpdate(BaseModel):
    type: RepositoryType | None = Field(
        default=None
    )
    url: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        pattern=r"^https?://"
    )
    project_id: int | None = Field(
        default=None,
        gt=0
    )

class RepositoryRead(RepositoryBase):
    id:int
    model_config = ConfigDict(from_attributes=True)


