"""
SQLite-backed vector store with numpy cosine similarity search.
"""

from __future__ import annotations
import json
import sqlite3
import logging
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from config import DB_PATH, TOP_K

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A single search result with score and metadata."""
    text: str
    source_file: str
    chunk_index: int
    score: float


class VectorStore:
    """SQLite-based vector store. Stores embeddings as JSON blobs and
    performs brute-force cosine similarity search with numpy."""

    def __init__(self, db_path: Path = DB_PATH):
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _init_db(self) -> None:
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                text        TEXT    NOT NULL,
                source_file TEXT    NOT NULL,
                chunk_index INTEGER NOT NULL,
                embedding   TEXT    NOT NULL
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_source
            ON chunks(source_file)
        """)
        self._conn.commit()

    # ── Write ────────────────────────────────────────────────────────────
    def add(self, text: str, source_file: str, chunk_index: int,
            embedding: list[float]) -> None:
        assert self._conn is not None
        self._conn.execute(
            "INSERT INTO chunks (text, source_file, chunk_index, embedding) "
            "VALUES (?, ?, ?, ?)",
            (text, source_file, chunk_index, json.dumps(embedding)),
        )
        self._conn.commit()

    def add_batch(self, items: list[tuple[str, str, int, list[float]]]) -> None:
        """Batch insert: list of (text, source_file, chunk_index, embedding)."""
        assert self._conn is not None
        self._conn.executemany(
            "INSERT INTO chunks (text, source_file, chunk_index, embedding) "
            "VALUES (?, ?, ?, ?)",
            [(t, s, ci, json.dumps(e)) for t, s, ci, e in items],
        )
        self._conn.commit()

    # ── Read ─────────────────────────────────────────────────────────────
    def search(self, query_embedding: list[float],
               top_k: int = TOP_K) -> list[SearchResult]:
        """Brute-force cosine similarity search."""
        assert self._conn is not None
        rows = self._conn.execute(
            "SELECT text, source_file, chunk_index, embedding FROM chunks"
        ).fetchall()

        if not rows:
            return []

        query_vec = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return []
        query_vec /= query_norm

        results: list[SearchResult] = []
        for text, source_file, chunk_index, emb_json in rows:
            stored_vec = np.array(json.loads(emb_json), dtype=np.float32)
            stored_norm = np.linalg.norm(stored_vec)
            if stored_norm == 0:
                continue
            stored_vec /= stored_norm
            score = float(np.dot(query_vec, stored_vec))
            results.append(SearchResult(
                text=text, source_file=source_file,
                chunk_index=chunk_index, score=score,
            ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    # ── Utilities ────────────────────────────────────────────────────────
    def count(self) -> int:
        assert self._conn is not None
        row = self._conn.execute("SELECT COUNT(*) FROM chunks").fetchone()
        return row[0] if row else 0

    def clear(self) -> None:
        assert self._conn is not None
        self._conn.execute("DELETE FROM chunks")
        self._conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
