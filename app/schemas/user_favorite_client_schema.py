from pydantic import BaseModel, ConfigDict


class UserFavoriteClientRead(BaseModel):
    user_id: int
    client_id: int

    model_config = ConfigDict(from_attributes=True)


class UserFavoriteClientAccess(BaseModel):
    client_id: int
