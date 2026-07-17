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

    QUEUE_PROVIDER: str = Field(
        default="memory",
        description="Background queue provider: 'memory' (in-process) or 'redis' (arq, future).",
    )
    MOCK_EXTRACTION_DELAY_SECONDS: float = Field(
        default=3.0,
        description="Simulated processing time for the mocked extraction worker.",
        ge=0.0,
    )
    CHUNK_SIZE: int = Field(
        default=500,
        description="Target character length per text chunk.",
        gt=0,
    )
    CHUNK_OVERLAP: int = Field(
        default=50,
        description="Overlap in characters between consecutive chunks.",
        ge=0,
    )
    ENTITY_EXTRACTOR: str = Field(
        default="rule",
        description="Entity extractor provider: 'rule' (local rule-based) or 'llm' (future).",
    )
    ENTITY_KEYWORDS: str = Field(
        default="Project,API,Report,Summary,Analysis,Database",
        description="Comma-separated high-value keywords for the rule-based extractor.",
    )


@lru_cache
def get_settings() -> Settings:
    # Settings() reads required fields from the environment; mypy strict cannot
    # see pydantic-settings' env injection, so the call-arg check is suppressed.
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
