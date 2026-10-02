from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.security.models.user_model import RoleType


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserLogin(BaseModel):
    email: EmailStr =Field(
        min_length=1,
        max_length=120
    )
    password: str = Field(
        min_length=10,
        max_length=120
    )


class UserRegister(BaseModel):
    email: EmailStr = Field(
        min_length=1,
        max_length=120
    )
    username: str = Field(
        min_length=1,
        max_length=120
    )
    password: str = Field(
        min_length=10,
        max_length=120
    )


class AdminUserCreate(UserRegister):
    role: RoleType = RoleType.GUEST
    is_active: bool = True

class UserSelfUpdate(BaseModel):
    email: EmailStr | None = Field(
        default=None,
        min_length=1,
        max_length=120
    )
    username: str | None = Field(
        default=None,
        min_length=1,
        max_length=120
    )

class AdminUserUpdate(UserSelfUpdate):
    role: RoleType | None = Field(
        default=None
    )
    is_active: bool | None = Field(
        default=None
    )


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)



class PasswordChange(BaseModel):
    current_password: str = Field(
        min_length=10,
        max_length=120
    )
    new_password: str = Field(
        min_length=10,
        max_length=120
    )