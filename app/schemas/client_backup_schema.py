from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from app.models.environment import EnvironmentType
from app.models.repository import RepositoryType
from app.schemas.client_schema import ClientBase
from app.schemas.project_schema import (
    CommandInProjectCreate,
    DomainInProjectCreate,
    EnvironmentInProjectCreate,
    LinkInProjectCreate,
    RepositoryInProjectCreate,
    ServiceInProjectCreate,
)

#Versiones para cambios futuros
JSON_BACKUP_SCHEMA_VERSION = 1
CSV_BACKUP_SCHEMA_VERSION = 1
#Solo aceptar esos 2 formatos
BackupFormat = Literal["json", "csv"]

BackupIdentifier = StrictInt


PROJECT_RESOURCE_COLLECTIONS = {
    "environment": "environments",
    "repository": "repositories",
    "domain": "domains",
    "link": "links",
    "service": "services",
    "command": "commands",
    "note": "notes",
}



class BackupRecord(BaseModel):
    #no permite atributos extra ni atributos de diferente tipo (ej: id:"12" X  -> id:12)
    model_config = ConfigDict(from_attributes=True, extra="forbid", strict=True)
    id: BackupIdentifier


class BackupClientDetails(ClientBase, BackupRecord):
    # La copia exige la clave cif incluso si su valor es null.
    cif: str | None = Field(max_length=120)
    is_active: bool


class BackupTag(BackupRecord):
    tag_type: str = Field(max_length=50)
    brand: str = Field(max_length=50)
    model: str = Field(max_length=100)
    mac: str | None = Field(max_length=255)
    ip: str | None = Field(max_length=255)


class BackupEnvironment(EnvironmentInProjectCreate, BackupRecord):
    type: EnvironmentType = Field(strict=False)


class BackupRepository(RepositoryInProjectCreate, BackupRecord):
    type: RepositoryType = Field(strict=False)


class BackupDomain(DomainInProjectCreate, BackupRecord):
    pass


class BackupLink(LinkInProjectCreate, BackupRecord):
    pass


class BackupService(ServiceInProjectCreate, BackupRecord):
    pass


class BackupCommand(CommandInProjectCreate, BackupRecord):
    pass


class BackupNote(BackupRecord):
    description: str = Field(max_length=255)
    content:  str = Field(min_length=1,max_length=5000)


class BackupProject(BackupRecord):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None,max_length=500)
    is_active: bool
    environments: list[BackupEnvironment]
    repositories: list[BackupRepository]
    domains: list[BackupDomain]
    links: list[BackupLink]
    services: list[BackupService]
    commands: list[BackupCommand]
    notes: list[BackupNote]


class ClientBackup(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    schema_version: int = Field(ge=JSON_BACKUP_SCHEMA_VERSION, le=JSON_BACKUP_SCHEMA_VERSION)
    client: BackupClientDetails
    tags: list[BackupTag]
    projects: list[BackupProject]


class BackupImportResult(BaseModel):
    client_id: int
    created: int = 0
    updated: int = 0
    deleted: int = 0
    linked: int = 0


class UnassignedBackupProject(BaseModel):
    id: int
    name: str


class BackupImportError(BaseModel):
    code: str
    message: str
    location: str | None = None
    projects: list[UnassignedBackupProject] | None = None
