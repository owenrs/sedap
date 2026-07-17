from enum import Enum
from functools import lru_cache

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    development = "development"
    test = "test"
    production = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: AppEnv = Field(default=AppEnv.development)

    DATABASE_URL: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection URI (postgresql://user:pass@host:port/db).",
    )

    SECRET_KEY: str = Field(
        ...,
        description="Signing key for JWT/sessions. Required — no insecure default.",
        min_length=1,
    )

    OPENAI_API_KEY: str | None = Field(default=None)
    CORS_ORIGINS: str = Field(default="")
    FRONTEND_URL: str | None = Field(default=None)


@lru_cache
def get_settings() -> Settings:
    # Settings() reads required fields from the environment; mypy strict cannot
    # see pydantic-settings' env injection, so the call-arg check is suppressed.
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
