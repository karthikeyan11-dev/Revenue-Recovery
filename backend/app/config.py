import logging
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("app.config")

# Strict path pointing exclusively to backend/.env
BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
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
        default="postgresql://postgres:postgres@localhost:5433/revenue_recovery",
        description="PostgreSQL or SQLite database connection URL",
    )

    # Multi-Provider LLM Configuration
    LLM_PROVIDER: str = Field(
        default="anthropic",
        description="LLM provider: 'anthropic', 'openai', 'google', or 'mock'",
    )
    MODEL: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Model name/identifier for reasoning tasks across all agents",
    )

    # Provider API Keys
    ANTHROPIC_API_KEY: str = Field(
        default="",
        description="API Key for Anthropic Claude models",
    )
    OPENAI_API_KEY: str = Field(
        default="",
        description="API Key for OpenAI GPT models",
    )
    GOOGLE_API_KEY: str = Field(
        default="",
        description="API Key for Google Gemini models",
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

    @field_validator("LLM_PROVIDER")
    @classmethod
    def validate_provider_name(cls, v: str) -> str:
        provider = v.strip().lower()
        allowed = {"anthropic", "openai", "google", "mock"}
        if provider not in allowed:
            raise ValueError(
                f"Unsupported LLM_PROVIDER '{v}'. Must be one of: {', '.join(sorted(allowed))}"
            )
        return provider

    def get_active_api_key(self) -> str:
        """Returns the API key corresponding to the currently configured provider."""
        provider = self.LLM_PROVIDER.strip().lower()
        if provider == "anthropic":
            return self.ANTHROPIC_API_KEY.strip()
        elif provider == "openai":
            return self.OPENAI_API_KEY.strip()
        elif provider == "google":
            return self.GOOGLE_API_KEY.strip()
        elif provider == "mock":
            return "mock-key"
        return ""

    def validate_llm_config(self) -> None:
        """Validates that the required API key for the selected provider is present."""
        provider = self.LLM_PROVIDER.strip().lower()
        key = self.get_active_api_key()

        if provider in {"anthropic", "openai", "google"}:
            if not key or key.startswith("mock-dev-key") or "your_" in key:
                logger.warning(
                    f"Selected LLM_PROVIDER '{provider}' has no active API key configured. "
                    "Inference calls will gracefully use contextual fallback templates."
                )
            else:
                masked_key = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
                logger.info(
                    f"Active LLM Configuration: provider={provider} | model={self.MODEL} | key={masked_key}"
                )


def get_settings() -> Settings:
    # Always reload fresh from backend/.env if changed
    return Settings()


settings = get_settings()
