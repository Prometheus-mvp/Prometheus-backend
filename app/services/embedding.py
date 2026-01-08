"""Embedding service using OpenAI and VectorStore."""

from __future__ import annotations

import asyncio
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings
from app.services.vector import VectorStore


def compute_content_hash(text: str) -> str:
    """Compute SHA256 hash for idempotency."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def chunk_text(text: str, max_chars: int = 3500) -> List[str]:
    """Simple character-based chunking to avoid overly long payloads."""
    if len(text) <= max_chars:
        return [text]
    chunks: List[str] = []
    for i in range(0, len(text), max_chars):
        chunks.append(text[i : i + max_chars])
    return chunks


@dataclass
class EmbeddingObject:
    """Embedding payload for a single object."""

    user_id: str
    object_type: str
    object_id: str
    text: str
    content_hash: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    occurred_at: Optional[datetime] = None  # For recency score calculation


class EmbeddingService:
    """OpenAI embedding service with VectorStore integration."""

    def __init__(
        self,
        *,
        model: str = "text-embedding-ada-002",
        vector_store: Optional[VectorStore] = None,
    ):
        self.model = model
        self.vector_store = vector_store or VectorStore()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def embed_text(self, texts: Sequence[str]) -> List[List[float]]:
        """Call OpenAI embeddings API with basic retry and timeout."""
        attempts = 3
        for attempt in range(attempts):
            try:
                resp = await self.client.embeddings.create(
                    model=self.model, input=list(texts), timeout=30
                )
                return [item.embedding for item in resp.data]
            except OpenAIError as exc:
                if attempt == attempts - 1:
                    self.logger.error(
                        "Embedding request failed", extra={"error": str(exc)}
                    )
                    raise RuntimeError("Embedding request failed") from exc
                await asyncio.sleep(0.5 * (attempt + 1))
            except Exception as exc:
                self.logger.error(
                    "Embedding response parsing failed", extra={"error": str(exc)}
                )
                raise RuntimeError("Embedding response invalid") from exc

    async def embed_and_store(
        self,
        session,
        objects: Sequence[EmbeddingObject],
        chunk_size_chars: int = 3500,
    ) -> int:
        """
        Generate embeddings for given objects and store via VectorStore.
        Skips objects if hashes match existing rows.
        Calculates recency_score based on occurred_at timestamp.
        """
        total = 0
        for obj in objects:
            text = obj.text or ""
            if not text.strip():
                continue
            content_hash = obj.content_hash or compute_content_hash(text)
            chunks = chunk_text(text, max_chars=chunk_size_chars)
            embeddings = await self.embed_text(chunks)
            for idx, emb in enumerate(embeddings):
                await self.vector_store.store_embedding(
                    session,
                    user_id=obj.user_id,
                    object_type=obj.object_type,
                    object_id=obj.object_id,
                    chunk_index=idx,
                    embedding=emb,
                    embedding_model=self.model,
                    content_hash=content_hash,
                    metadata=obj.metadata or {},
                    occurred_at=obj.occurred_at,  # For recency score calculation
                )
                total += 1
        return total


__all__ = ["EmbeddingService", "EmbeddingObject", "compute_content_hash", "chunk_text"]
