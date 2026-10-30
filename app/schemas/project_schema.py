from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.environment import EnvironmentType
from app.models.repository import RepositoryType
from app.schemas.client_schema import ClientRead, ClientCreate
from app.schemas.command_schema import CommandRead
from app.schemas.domain_schema import DomainRead
from app.schemas.environment_schema import EnvironmentRead
from app.schemas.link_schema import LinkRead
from app.schemas.note_schema import NoteRead
from app.schemas.repository_schema import RepositoryRead
from app.schemas.service_schema import ServiceRead


class ProjectBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=120,
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    client_id: int | None = Field(default=None, gt=0)


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
    client_id: int | None = Field(
        default=None,
    )


class ProjectRead(ProjectBase):
    id: int
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class ProjectLightRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ClientTableRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class EnvironmentTableRead(BaseModel):
    id: int
    type: EnvironmentType
    url: str

    model_config = ConfigDict(from_attributes=True)


class RepositoryTableRead(BaseModel):
    id: int
    type: RepositoryType
    url: str

    model_config = ConfigDict(from_attributes=True)


class ServiceTableRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class DomainTableRead(BaseModel):
    id: int
    url: str

    model_config = ConfigDict(from_attributes=True)


class ProjectTableRead(BaseModel):
    id: int
    name: str
    client: ClientTableRead | None
    environments: list[EnvironmentTableRead]
    repositories: list[RepositoryTableRead]
    services: list[ServiceTableRead]
    domains: list[DomainTableRead]
    commands_count: int
    links_count: int
    notes_count: int

    model_config = ConfigDict(from_attributes=True)


class PaginatedProjectTableRead(BaseModel):
    items: list[ProjectTableRead]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)


class ProjectDetailRead(ProjectRead):
    client: ClientRead | None
    environments: list[EnvironmentRead]
    repositories: list[RepositoryRead]
    domains: list[DomainRead]
    links: list[LinkRead]
    services: list[ServiceRead]
    commands: list[CommandRead]
    notes: list[NoteRead]


class EnvironmentInProjectCreate(BaseModel):
    type: EnvironmentType
    url: str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^https?://",
    )


class RepositoryInProjectCreate(BaseModel):
    type: RepositoryType
    url: str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^https?://",
    )


class ServiceInProjectCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )


class DomainInProjectCreate(BaseModel):
    url: str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^https?://",
    )


class CommandInProjectCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )
    instruction: str = Field(
        min_length=1,
        max_length=255,
    )


class LinkInProjectCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )
    url: str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^https?://",
    )


class NoteInProjectCreate(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=255,
    )
    content: str = Field(
        min_length=1,
        max_length=5000,
    )


class ProjectFullCreate(ProjectBase):
    is_active: bool = True

    client_id: int | None = None
    client: ClientCreate | None = None

    environments: list[EnvironmentInProjectCreate] = Field(default_factory=list)
    repositories: list[RepositoryInProjectCreate] = Field(default_factory=list)
    services: list[ServiceInProjectCreate] = Field(default_factory=list)
    domains: list[DomainInProjectCreate] = Field(default_factory=list)
    commands: list[CommandInProjectCreate] = Field(default_factory=list)
    links: list[LinkInProjectCreate] = Field(default_factory=list)
    notes: list[NoteInProjectCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_client(self):
        if self.client is not None and self.client_id is not None:
            raise ValueError(
                "Indica un cliente existente o los datos de un cliente nuevo, no ambos."
            )
        return self
