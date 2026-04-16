"""
Configuración de la aplicación vía variables de entorno.
Ref: context/restrictions.md RES-C01 — nunca hardcoded en código fuente.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Base de datos
    database_url: str = "sqlite+aiosqlite:///./motor_dev.db"

    # JWT
    secret_key: str = "dev-only-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # App
    debug: bool = False
    app_name: str = "Motor de Cumplimiento Colombia"
    app_version: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
