"""
Vision handler — image captioning and tagging using Gemini Vision.
"""

from __future__ import annotations
import io
import logging
from dataclasses import dataclass
from PIL import Image
from google import genai
from config import GEMINI_API_KEY, GEMINI_VISION_MODEL

logger = logging.getLogger(__name__)


@dataclass
class ImageAnalysis:
    """Result of an image analysis."""
    caption: str
    tags: list[str]
    raw_response: str


class VisionHandler:
    """Handles image analysis using Gemini Vision."""

    def __init__(self, api_key: str = GEMINI_API_KEY,
                 model: str = GEMINI_VISION_MODEL):
        self._model = model
        self._client = genai.Client(api_key=api_key)
        logger.info("Vision handler initialised with model: %s", model)

    async def analyze_image(self, image_bytes: bytes) -> ImageAnalysis:
        """Analyze an image and return caption + tags."""
        try:
            # Load and validate image
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode == "RGBA":
                image = image.convert("RGB")

            prompt = (
                "Analyze this image and provide:\n"
                "1. A short, descriptive caption (1-2 sentences)\n"
                "2. Exactly 3 relevant keyword tags\n\n"
                "Format your response EXACTLY like this:\n"
                "CAPTION: <your caption here>\n"
                "TAGS: <tag1>, <tag2>, <tag3>"
            )

            response = self._client.models.generate_content(
                model=self._model,
                contents=[prompt, image],
                config=genai.types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=256,
                ),
            )

            raw = response.text or ""
            caption, tags = self._parse_response(raw)

            return ImageAnalysis(caption=caption, tags=tags, raw_response=raw)

        except Exception as e:
            logger.error("Vision analysis failed: %s", e)
            return ImageAnalysis(
                caption=f"⚠️ Error analysing image: {e}",
                tags=[],
                raw_response="",
            )

    @staticmethod
    def _parse_response(text: str) -> tuple[str, list[str]]:
        """Parse the structured response into caption and tags."""
        caption = ""
        tags: list[str] = []

        for line in text.strip().splitlines():
            line = line.strip()
            upper = line.upper()
            if upper.startswith("CAPTION:"):
                caption = line[len("CAPTION:"):].strip()
            elif upper.startswith("TAGS:"):
                tag_str = line[len("TAGS:"):].strip()
                tags = [t.strip() for t in tag_str.split(",") if t.strip()]

        # Fallback if parsing fails
        if not caption:
            caption = text.strip().split("\n")[0] if text.strip() else "No caption generated."
        if not tags:
            tags = ["untagged"]

        return caption, tags
