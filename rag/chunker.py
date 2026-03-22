"""
Document chunker — splits markdown files into overlapping text chunks.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from config import CHUNK_SIZE, CHUNK_OVERLAP, KNOWLEDGE_BASE_DIR


@dataclass
class Chunk:
    """A chunk of text with source metadata."""
    text: str
    source_file: str
    chunk_index: int


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks based on character count,
    breaking on paragraph boundaries when possible."""
    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph exceeds chunk_size, save current and start new
        if current_chunk and len(current_chunk) + len(para) + 2 > chunk_size:
            chunks.append(current_chunk.strip())
            # Keep overlap from the end of the current chunk
            if overlap > 0 and len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:] + "\n\n" + para
            else:
                current_chunk = para
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def chunk_file(filepath: Path,
               chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list[Chunk]:
    """Read a file and return a list of Chunks."""
    text = filepath.read_text(encoding="utf-8")
    raw_chunks = _split_text(text, chunk_size, overlap)
    return [
        Chunk(text=c, source_file=filepath.name, chunk_index=i)
        for i, c in enumerate(raw_chunks)
    ]


def chunk_all_documents(directory: Path = KNOWLEDGE_BASE_DIR,
                        chunk_size: int = CHUNK_SIZE,
                        overlap: int = CHUNK_OVERLAP) -> list[Chunk]:
    """Chunk every .md and .txt file in the knowledge base directory."""
    all_chunks: list[Chunk] = []
    for ext in ("*.md", "*.txt"):
        for filepath in sorted(directory.glob(ext)):
            all_chunks.extend(chunk_file(filepath, chunk_size, overlap))
    return all_chunks
