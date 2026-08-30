import logging

from pydantic import BaseModel, Field

from app.config import settings
from app.integrations.llm.factory import get_llm_provider

logger = logging.getLogger("app.integrations.llm.client")


class LLMReasoningResponse(BaseModel):
    reasoning: str = Field(description="Contextual natural-language rationale")


class LLMClient:
    """
    Provider-Agnostic LLM Reasoning Engine with robust fallback handling.
    Executes real inference using the configured provider (Anthropic / OpenAI / Google / Mock);
    gracefully falls back to deterministic contextual templates if offline, uncredited, or misconfigured.
    """

    _circuit_broken_until: float = 0.0

    @classmethod
    def generate_reasoning(
        cls,
        system_prompt: str,
        user_prompt: str,
        fallback_text: str,
        max_tokens: int = 150,
    ) -> str:
        provider_name = settings.LLM_PROVIDER.strip().lower()
        active_key = settings.get_active_api_key()

        # If running in mock provider mode
        if provider_name == "mock":
            try:
                provider = get_llm_provider("mock", settings.MODEL, "mock-key")
                text = provider.generate_reasoning(system_prompt, user_prompt, max_tokens)
                return LLMReasoningResponse(reasoning=text).reasoning
            except Exception as e:
                logger.warning(f"Mock provider error: {e}")
                return fallback_text

        # Check circuit breaker (if rate-limited recently, use contextual fallback immediately)
        import time

        if time.time() < cls._circuit_broken_until:
            return fallback_text

        # Check for unconfigured / placeholder keys
        if not active_key or active_key.startswith("mock-dev-key") or "your_" in active_key:
            logger.debug(
                f"No valid API key configured for '{provider_name}'. Using contextual reasoning fallback."
            )
            return fallback_text

        try:
            provider = get_llm_provider(provider_name, settings.MODEL, active_key)
            raw_text = provider.generate_reasoning(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
            )

            if raw_text:
                res = LLMReasoningResponse(reasoning=raw_text)
                logger.info(f"✓ LLM reasoning generated via {provider_name} ({settings.MODEL})")
                return res.reasoning

            return fallback_text

        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "rate limit" in err_msg.lower():
                cls._circuit_broken_until = time.time() + 60.0  # Trip circuit for 60s

            # Mask any credentials from exception messages
            if active_key and active_key in err_msg:
                err_msg = err_msg.replace(active_key, "***")

            logger.warning(
                f"{provider_name.capitalize()} API call failed ({type(e).__name__}: {err_msg}). "
                "Using high-fidelity contextual fallback."
            )
            return fallback_text
