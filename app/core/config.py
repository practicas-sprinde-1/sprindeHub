# Esta clase es la configuracion principal de la bdd en la cual se extraen los datos del archivo .env
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

ENV_FILE_PATH = os.getenv("ENV_FILE", ".env")

class Settings(BaseSettings):
    app_name: str = "Sprinde_App"
    environment: str = "development"

    database_url:str

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_issuer: str
    jwt_audience: str

    access_token_minutes: int
    refresh_token_days: int

    cors_origins: list[str] = []

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="ignore"
    )



# Instanciamos la configuración (aquí es donde se lee el .env y se valida todo)
@lru_cache
def get_settings()->Settings:
    return Settings()

settings = get_settings()
