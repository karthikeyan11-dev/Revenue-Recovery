from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """
    Abstract Base Class defining the unified provider-agnostic interface for LLM reasoning.
    All providers (Anthropic, OpenAI, Google Gemini, Mock) implement this interface.
    """

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def generate_reasoning(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 150,
    ) -> str:
        """
        Executes inference against the underlying provider API and returns the generated text.
        Raises an exception if the API call fails so that fallback handlers can intervene.
        """
        pass
