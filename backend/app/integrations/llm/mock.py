import logging

from app.integrations.llm.base import BaseLLMProvider

logger = logging.getLogger("app.integrations.llm.mock")


class MockProvider(BaseLLMProvider):
    """
    Deterministic Mock Provider for offline tests, sandboxes, and development.
    """

    def __init__(self, model: str = "mock-model", api_key: str = "mock-key"):
        super().__init__(model=model, api_key=api_key)

    def generate_reasoning(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 150,
    ) -> str:
        return f"[MockLLM Reasoning - {self.model}]: Analyzed telemetry and formulated optimal recovery strategy."
