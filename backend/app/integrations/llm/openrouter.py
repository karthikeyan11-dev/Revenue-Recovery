import logging

import openai

from app.integrations.llm.base import BaseLLMProvider

logger = logging.getLogger("app.integrations.llm.openrouter")


class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter Unified Multi-Model Provider implementation.
    Routes requests to 300+ AI models (Google Gemini, Anthropic Claude, OpenAI GPT, DeepSeek, Llama)
    via OpenRouter's OpenAI-compatible API endpoint.
    """

    def __init__(self, model: str, api_key: str):
        super().__init__(model=model, api_key=api_key)
        if not api_key or api_key.startswith("your_") or api_key.startswith("mock-dev-key"):
            raise ValueError("OPENROUTER_API_KEY is required for OpenRouterProvider")

        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=3.0,
            max_retries=0,
            default_headers={
                "HTTP-Referer": "https://github.com/karthikeyan11-dev/Revenue-Recovery",
                "X-Title": "AI Revenue Recovery Orchestrator",
            },
        )

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
