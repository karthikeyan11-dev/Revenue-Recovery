import logging

import openai

from app.integrations.llm.base import BaseLLMProvider

logger = logging.getLogger("app.integrations.llm.openai")


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI GPT Provider implementation.
    """

    def __init__(self, model: str, api_key: str):
        super().__init__(model=model, api_key=api_key)
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIProvider")
        self.client = openai.OpenAI(api_key=api_key, timeout=5.0)

    def generate_reasoning(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 150,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        if response.choices and len(response.choices) > 0:
            return (response.choices[0].message.content or "").strip()
        return ""
