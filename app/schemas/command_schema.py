from pydantic import BaseModel, Field, ConfigDict

class CommandBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )
    project_id: int = Field(gt=0)

    instruction: str = Field(
        min_length=1,
        max_length=255,
    )

class CommandCreate(CommandBase):
    pass

class CommandUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    project_id: int | None = Field(
        default=None,
        gt=0
    )
    instruction: str |None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

class CommandRead(CommandBase):
    id:int
    model_config = ConfigDict(from_attributes=True)


