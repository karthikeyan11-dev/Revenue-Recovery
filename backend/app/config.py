import logging
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "AI Revenue Recovery Orchestrator"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/revenue_recovery",
        description="PostgreSQL or SQLite database connection URL",
    )

    # LLM Settings
    LLM_PROVIDER: str = Field(
        default="anthropic",
        description="LLM provider name (anthropic / openai)",
    )
    ANTHROPIC_API_KEY: str = Field(
        default="",
        description="API Key for Anthropic API",
    )
    MODEL: str = Field(
        default="claude-sonnet-4-6",
        description="Model name to use for agent reasoning",
    )

    # CORS
    CORS_ORIGINS: str | list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
        description="Allowed CORS origins as a list or comma-separated string",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [i.strip() for i in self.CORS_ORIGINS.split(",") if i.strip()]
        return self.CORS_ORIGINS

    def validate_llm_config(self) -> None:
        """Explicit check for LLM keys when agent features are invoked."""
        if not self.ANTHROPIC_API_KEY or self.ANTHROPIC_API_KEY.startswith("mock-dev-key"):
            logging.warning(
                "ANTHROPIC_API_KEY is not set or using mock placeholder. "
                "Agent LLM reasoning calls will require a valid key."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
