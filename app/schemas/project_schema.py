from pydantic import BaseModel, ConfigDict, Field

from app.schemas.client_schema import ClientRead
from app.schemas.command_schema import CommandRead
from app.schemas.environment_schema import EnvironmentRead
from app.schemas.domain_schema import DomainRead
from app.schemas.link_schema import LinkRead
from app.schemas.note_schema import NoteRead
from app.schemas.repository_schema import RepositoryRead
from app.schemas.service_schema import ServiceRead

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

class ClientTableRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class EnvironmentTableRead(BaseModel):
    id: int
    type: str
    url: str

    model_config = ConfigDict(from_attributes=True)


class RepositoryTableRead(BaseModel):
    id: int
    type: str
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
    client: ClientTableRead
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

    client: ClientRead
    environments: list[EnvironmentRead]
    repositories: list[RepositoryRead]
    domains: list[DomainRead]
    links: list[LinkRead]
    services: list[ServiceRead]
    commands: list[CommandRead]
    notes: list[NoteRead]
