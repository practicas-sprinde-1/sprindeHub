from pydantic import BaseModel, Field, ConfigDict

class LinkBase(BaseModel):
    url: str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^https?://"
    )
    project_id: int = Field(gt=0)

    title: str = Field(
        min_length=1,
        max_length=255,
    )

class LinkCreate(LinkBase):
    pass

class LinkUpdate(BaseModel):
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
    title: str |None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

class LinkRead(LinkBase):
    id:int
    model_config = ConfigDict(from_attributes=True)


