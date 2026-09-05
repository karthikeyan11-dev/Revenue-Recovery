import logging

from google import genai
from google.genai import types

from app.integrations.llm.base import BaseLLMProvider

logger = logging.getLogger("app.integrations.llm.google")


class GoogleProvider(BaseLLMProvider):
    """
    Google Gemini Provider implementation using official google-genai SDK.
    """

    def __init__(self, model: str, api_key: str):
        super().__init__(model=model, api_key=api_key)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is required for GoogleProvider")
        self.client = genai.Client(api_key=api_key)

    def generate_reasoning(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 150,
    ) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=max_tokens,
                temperature=0.2,
            ),
        )
        return (response.text or "").strip()
