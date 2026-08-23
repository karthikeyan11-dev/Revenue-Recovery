import logging
from functools import lru_cache

from app.config import get_settings
from app.llm.anthropic_provider import AnthropicProvider
from app.llm.base import BaseLLMProvider
from app.llm.google_provider import GoogleProvider
from app.llm.mock_provider import MockProvider
from app.llm.openai_provider import OpenAIProvider

logger = logging.getLogger("app.llm.factory")


@lru_cache(maxsize=16)
def _create_provider_instance(provider: str, model: str, key: str) -> BaseLLMProvider:
    """Internal cached builder keyed explicitly by provider, model, and key."""
    masked_key = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else ("***" if key else "EMPTY")
    logger.info(f"Instantiating LLM Provider: '{provider}' (model: '{model}', key: {masked_key})")

    if provider == "anthropic":
        return AnthropicProvider(model=model, api_key=key)
    elif provider == "openai":
        return OpenAIProvider(model=model, api_key=key)
    elif provider == "google":
        return GoogleProvider(model=model, api_key=key)
    elif provider == "mock":
        return MockProvider(model=model, api_key=key)
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER '{provider}'. Supported providers are: anthropic, openai, google, mock"
        )


def get_llm_provider(
    provider_name: str | None = None,
    model_name: str | None = None,
    api_key: str | None = None,
) -> BaseLLMProvider:
    """
    Factory function to retrieve the configured LLM provider.
    Always reads current settings dynamically from backend/.env.
    """
    current_settings = get_settings()
    provider = (provider_name or current_settings.LLM_PROVIDER).strip().lower()
    model = (model_name or current_settings.MODEL).strip()
    key = (api_key or current_settings.get_active_api_key()).strip()

    return _create_provider_instance(provider, model, key)
