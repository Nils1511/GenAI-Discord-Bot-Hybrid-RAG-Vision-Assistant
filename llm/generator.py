"""
LLM generator — wraps the Google Gemini API for text generation.
"""

from __future__ import annotations
import logging
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)


class LLMGenerator:
    """Async wrapper around the Gemini API."""

    def __init__(self, api_key: str = GEMINI_API_KEY,
                 model: str = GEMINI_MODEL):
        self._model = model
        self._client = genai.Client(api_key=api_key)
        logger.info("LLM generator initialised with model: %s", model)

    async def generate(self, prompt: str,
                       temperature: float = 0.3,
                       max_tokens: int = 1024) -> str:
        """Generate a text response from the given prompt."""
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )
            text = response.text
            if not text:
                return "I received an empty response from the model. Please try again."
            return text.strip()
        except Exception as e:
            logger.error("LLM generation failed: %s", e)
            return f"⚠️ Error generating response: {e}"

    async def summarize(self, text: str) -> str:
        """Generate a concise summary of the given text."""
        prompt = (
            "Provide a concise summary (2-3 sentences) of the following content. "
            "Focus on key information and main points.\n\n"
            f"Content:\n{text}\n\nSummary:"
        )
        return await self.generate(prompt, temperature=0.2)
