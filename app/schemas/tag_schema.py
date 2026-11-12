from pydantic import BaseModel, ConfigDict, Field, field_validator


class _TagFields(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("device_type", "brand", "model", mode="before", check_fields=False)
    @classmethod
    def validate_required_text(cls, value):
        if value is None:
            raise ValueError("El campo no puede ser null.")
        return value.strip() if isinstance(value, str) else value

    @field_validator("mac", "ip", mode="before", check_fields=False)
    @classmethod
    def normalize_optional_text(cls, value):
        if isinstance(value, str):
            return value.strip() or None
        return value


class TagBase(_TagFields):
    device_type: str = Field(min_length=1, max_length=50)
    brand: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=100)
    client_id: int = Field(gt=0)
    mac: str | None = Field(default=None, max_length=255)
    ip: str | None = Field(default=None, max_length=255)


class TagCreate(TagBase):
    pass


class TagUpdate(_TagFields):
    device_type: str | None = Field(default=None, min_length=1, max_length=50)
    brand: str | None = Field(default=None, min_length=1, max_length=50)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    mac: str | None = Field(default=None, max_length=255)
    ip: str | None = Field(default=None, max_length=255)


class TagRead(TagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
