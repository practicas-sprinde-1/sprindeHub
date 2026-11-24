from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    tag_type: str = Field(min_length=1, max_length=50)
    brand: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=100)
    client_id: int = Field(gt=0)
    mac: str | None = Field(default=None, max_length=255)
    ip: str | None = Field(default=None, max_length=255)


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    tag_type: str | None = Field(default=None, min_length=1, max_length=50)
    brand: str | None = Field(default=None, min_length=1, max_length=50)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    mac: str | None = Field(default=None, max_length=255)
    ip: str | None = Field(default=None, max_length=255)


class TagRead(TagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
