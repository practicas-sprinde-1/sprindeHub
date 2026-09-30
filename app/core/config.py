# Esta clase es la configuracion principal de la bdd en la cual se extraen los datos del archivo .env
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = os.getenv("ENV_FILE", ".env")


class Settings(BaseSettings):
    database_url: str
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ENV_FILE, extra="ignore")


# Instanciamos la configuración (aquí es donde se lee el .env y se valida todo)
settings = Settings()
