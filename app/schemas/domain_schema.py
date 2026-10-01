from pydantic import BaseModel, Field, ConfigDict

class DomainBase(BaseModel):
    url: str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^https?://"
    )
    project_id: int = Field(gt=0)

class DomainCreate(DomainBase):
    pass

class DomainUpdate(BaseModel):
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

class DomainRead(DomainBase):
    id:int
    model_config = ConfigDict(from_attributes=True)


