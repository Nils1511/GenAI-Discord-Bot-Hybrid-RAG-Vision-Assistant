"""
Embedding module — wraps sentence-transformers for text embedding.
"""

from __future__ import annotations
import logging
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)


class Embedder:
    """Lazy-loaded sentence-transformer embedder."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self._model_name = model_name
        self._model: SentenceTransformer | None = None

    def _load(self) -> SentenceTransformer:
        if self._model is None:
            logger.info("Loading embedding model: %s", self._model_name)
            self._model = SentenceTransformer(self._model_name)
            logger.info("Embedding model loaded successfully.")
        return self._model

    def embed(self, text: str) -> list[float]:
        """Embed a single text string and return a list of floats."""
        model = self._load()
        vector = model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in a single batch."""
        model = self._load()
        vectors = model.encode(texts, normalize_embeddings=True, batch_size=32)
        return vectors.tolist()

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        model = self._load()
        return model.get_sentence_embedding_dimension()
