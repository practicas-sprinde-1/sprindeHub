from pydantic import BaseModel, Field, ConfigDict

class ServiceBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )
    project_id: int = Field(gt=0)

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    project_id: int | None = Field(
        default=None,
        gt=0
    )

class ServiceRead(ServiceBase):
    id:int
    model_config = ConfigDict(from_attributes=True)


