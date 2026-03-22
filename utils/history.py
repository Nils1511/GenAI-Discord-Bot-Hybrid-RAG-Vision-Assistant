"""
Per-user message history tracker.
Keeps the last N interactions (query + response) for context-aware replies.
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field
from config import MAX_HISTORY


@dataclass
class Interaction:
    """A single user interaction."""
    query: str
    response: str
    interaction_type: str = "text"       # "text" | "image"
    image_url: str | None = None


class HistoryManager:
    """Maintains a sliding window of interactions per user."""

    def __init__(self, max_history: int = MAX_HISTORY):
        self._max = max_history
        self._store: dict[int, deque[Interaction]] = defaultdict(
            lambda: deque(maxlen=self._max)
        )

    def add(self, user_id: int, interaction: Interaction) -> None:
        self._store[user_id].append(interaction)

    def get(self, user_id: int) -> list[Interaction]:
        return list(self._store[user_id])

    def get_last(self, user_id: int) -> Interaction | None:
        history = self._store.get(user_id)
        if history:
            return history[-1]
        return None

    def format_for_prompt(self, user_id: int) -> str:
        """Return conversation history formatted for an LLM prompt."""
        history = self.get(user_id)
        if not history:
            return ""
        lines = ["## Recent Conversation History"]
        for i, h in enumerate(history, 1):
            lines.append(f"**Turn {i} ({h.interaction_type})**")
            lines.append(f"- User: {h.query}")
            lines.append(f"- Assistant: {h.response[:300]}...")
        return "\n".join(lines)

    def clear(self, user_id: int) -> None:
        if user_id in self._store:
            self._store[user_id].clear()
