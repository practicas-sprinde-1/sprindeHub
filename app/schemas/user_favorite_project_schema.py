from pydantic import BaseModel, ConfigDict


class UserFavoriteProjectRead(BaseModel):
    user_id: int
    project_id: int

    model_config = ConfigDict(from_attributes=True)


class UserFavoriteProjectAccess(BaseModel):
    project_id: int
