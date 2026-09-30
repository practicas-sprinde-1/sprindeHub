from pydantic import BaseModel, Field, ConfigDict

class ProjectBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=120,
    )

    description:str | None= Field(
        default=None,
        max_length=500
    )

    client_id: int = Field(gt=0)

class ProjectCreate(ProjectBase):
   pass

class ProjectUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )
    client_id: int |None= Field(
        default=None,
        gt=0
    )

class ProjectRead(ProjectBase):
    id: int
    is_active:bool

    model_config = ConfigDict(
        from_attributes=True
    )
