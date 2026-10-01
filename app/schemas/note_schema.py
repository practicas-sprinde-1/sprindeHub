from pydantic import BaseModel, Field, ConfigDict

class NoteBase(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=255,
    )
    project_id: int = Field(gt=0)

    content: str = Field(
        min_length=1,
        max_length=5000,
    )

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    project_id: int | None = Field(
        default=None,
        gt=0
    )
    content: str |None = Field(
        default=None,
        min_length=1,
        max_length=5000,
    )

class NoteRead(NoteBase):
    id:int
    model_config = ConfigDict(from_attributes=True)


