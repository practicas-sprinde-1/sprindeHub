from pydantic import BaseModel, Field, ConfigDict

class UserClientRead(BaseModel):
    user_id:int
    client_id:int
    model_config = ConfigDict(from_attributes=True)

class UserClientAccess(BaseModel):
    client_id:int

