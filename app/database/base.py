"""Importa todos los modelos para registrarlos en los metadatos de SQLAlchemy."""

from app.models.client import Client
from app.models.tag import Tag
from app.models.command import Command
from app.models.domain import Domain
from app.models.environment import Environment
from app.models.link import Link
from app.models.note import Note
from app.models.project import Project
from app.models.repository import Repository
from app.models.service import Service
from app.security.models.log_model import Log
from app.security.models.user_client_model import UserClient
from app.models.user_favorite_client_model import UserFavoriteClient
from app.models.user_favorite_project_model import UserFavoriteProject
from app.security.models.user_model import User

# __all__ evita advertencias de "importación sin uso" en los linters y re-exporta los modelos.
__all__ = (
    "Client",
    "Tag",
    "Command",
    "Domain",
    "Environment",
    "Link",
    "Log",
    "Note",
    "Project",
    "Repository",
    "Service",
    "User",
    "UserClient",
    "UserFavoriteClient",
    "UserFavoriteProject",
)

