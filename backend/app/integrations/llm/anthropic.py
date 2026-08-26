import logging

import anthropic

from app.integrations.llm.base import BaseLLMProvider

logger = logging.getLogger("app.integrations.llm.anthropic")


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude Provider implementation.
    """

    def __init__(self, model: str, api_key: str):
        super().__init__(model=model, api_key=api_key)
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for AnthropicProvider")
        self.client = anthropic.Anthropic(api_key=api_key, timeout=5.0)

    def generate_reasoning(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 150,
    ) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=0.2,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        if message.content and len(message.content) > 0:
            return message.content[0].text.strip()
        return ""
