"""
Retriever — orchestrates the RAG pipeline:
  query → embed → search → build prompt → generate answer.
"""

from __future__ import annotations
import logging
from rag.chunker import chunk_all_documents
from rag.embedder import Embedder
from rag.vector_store import VectorStore, SearchResult
from llm.generator import LLMGenerator
from utils.cache import QueryCache
from config import TOP_K

logger = logging.getLogger(__name__)


class Retriever:
    """High-level RAG retriever."""

    def __init__(self, embedder: Embedder, store: VectorStore,
                 llm: LLMGenerator, cache: QueryCache):
        self._embedder = embedder
        self._store = store
        self._llm = llm
        self._cache = cache

    # ── Index ────────────────────────────────────────────────────────────
    def index_knowledge_base(self) -> int:
        """Chunk, embed, and store all documents. Returns chunk count."""
        if self._store.count() > 0:
            logger.info("Vector store already populated (%d chunks). Skipping indexing.",
                        self._store.count())
            return self._store.count()

        logger.info("Indexing knowledge base...")
        chunks = chunk_all_documents()
        if not chunks:
            logger.warning("No documents found in knowledge base.")
            return 0

        texts = [c.text for c in chunks]
        embeddings = self._embedder.embed_batch(texts)

        items = [
            (c.text, c.source_file, c.chunk_index, emb)
            for c, emb in zip(chunks, embeddings)
        ]
        self._store.add_batch(items)
        logger.info("Indexed %d chunks from %d documents.",
                     len(chunks), len({c.source_file for c in chunks}))
        return len(chunks)

    # ── Query ────────────────────────────────────────────────────────────
    async def query(self, question: str,
                    conversation_context: str = "",
                    top_k: int = TOP_K) -> tuple[str, list[SearchResult]]:
        """Run the full RAG pipeline. Returns (answer, sources)."""
        # Check response cache first
        cached = self._cache.get_response(question)
        if cached:
            logger.info("Cache hit for query: %s", question[:60])
            return cached, []

        # Embed the query (with caching)
        cached_emb = self._cache.get_embedding(question)
        if cached_emb:
            query_embedding = cached_emb
        else:
            query_embedding = self._embedder.embed(question)
            self._cache.put_embedding(question, query_embedding)

        # Retrieve relevant chunks
        results = self._store.search(query_embedding, top_k=top_k)

        if not results:
            return "I couldn't find any relevant information in my knowledge base.", []

        # Build context from retrieved chunks
        context_parts = []
        for i, r in enumerate(results, 1):
            context_parts.append(
                f"[Source {i}: {r.source_file} | Relevance: {r.score:.2f}]\n{r.text}"
            )
        retrieved_context = "\n\n---\n\n".join(context_parts)

        # Build the full prompt
        prompt = self._build_prompt(question, retrieved_context, conversation_context)

        # Generate answer
        answer = await self._llm.generate(prompt)

        # Cache the response
        self._cache.put_response(question, answer)

        return answer, results

    @staticmethod
    def _build_prompt(question: str, context: str,
                      conversation_context: str) -> str:
        parts = [
            "You are a helpful assistant. Answer the user's question using ONLY "
            "the provided context below. If the context doesn't contain enough "
            "information, say so honestly. Cite the source file when possible.\n",
        ]
        if conversation_context:
            parts.append(conversation_context + "\n")
        parts.append(f"## Retrieved Context\n{context}\n")
        parts.append(f"## User Question\n{question}\n")
        parts.append("## Your Answer (be concise and helpful):")
        return "\n".join(parts)
