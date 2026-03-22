"""
LRU-based query cache to avoid re-embedding identical queries.
"""

from collections import OrderedDict
from config import CACHE_MAX_SIZE


class QueryCache:
    """Simple LRU cache mapping query strings → (embedding, response)."""

    def __init__(self, max_size: int = CACHE_MAX_SIZE):
        self._max_size = max_size
        self._embedding_cache: OrderedDict[str, list[float]] = OrderedDict()
        self._response_cache: OrderedDict[str, str] = OrderedDict()

    # ── Embedding cache ──────────────────────────────────────────────────
    def get_embedding(self, query: str) -> list[float] | None:
        key = query.strip().lower()
        if key in self._embedding_cache:
            self._embedding_cache.move_to_end(key)
            return self._embedding_cache[key]
        return None

    def put_embedding(self, query: str, embedding: list[float]) -> None:
        key = query.strip().lower()
        self._embedding_cache[key] = embedding
        self._embedding_cache.move_to_end(key)
        if len(self._embedding_cache) > self._max_size:
            self._embedding_cache.popitem(last=False)

    # ── Response cache ───────────────────────────────────────────────────
    def get_response(self, query: str) -> str | None:
        key = query.strip().lower()
        if key in self._response_cache:
            self._response_cache.move_to_end(key)
            return self._response_cache[key]
        return None

    def put_response(self, query: str, response: str) -> None:
        key = query.strip().lower()
        self._response_cache[key] = response
        self._response_cache.move_to_end(key)
        if len(self._response_cache) > self._max_size:
            self._response_cache.popitem(last=False)

    def clear(self) -> None:
        self._embedding_cache.clear()
        self._response_cache.clear()
