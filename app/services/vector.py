"""VectorStore abstraction (pgvector implementation)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Embedding, Event


@dataclass
class VectorRecord:
    """Returned vector search record."""

    id: str
    object_type: str
    object_id: str
    chunk_index: int
    score: float  # Original cosine distance
    metadata: Dict[str, Any]
    recency_score: Optional[float] = None  # Stored recency score [0, 1]
    semantic_score: Optional[float] = None  # Normalized similarity [0, 1]
    final_score: Optional[float] = None  # Combined score


class VectorStore:
    """VectorStore abstraction with pgvector backend."""

    def __init__(self, embedding_dim: int = 1536, distance_metric: str = "cosine"):
        self.embedding_dim = embedding_dim
        self.distance_metric = distance_metric

    async def store_embedding(
        self,
        session: AsyncSession,
        *,
        user_id: str,
        object_type: str,
        object_id: str,
        chunk_index: int,
        embedding: Sequence[float],
        embedding_model: str,
        content_hash: str,
        metadata: Optional[Dict[str, Any]] = None,
        occurred_at: Optional[datetime] = None,
    ) -> None:
        """Upsert an embedding row with recency score calculation."""
        metadata = metadata or {}

        # Calculate recency score if occurred_at provided
        recency_score = None
        if occurred_at:
            now = datetime.now(timezone.utc)
            age_days = (now - occurred_at).total_seconds() / 86400
            tau_days = settings.ranking_tau_days
            recency_score = math.exp(-age_days / tau_days)

        stmt = (
            Embedding.__table__.insert()
            .values(
                user_id=user_id,
                object_type=object_type,
                object_id=object_id,
                chunk_index=chunk_index,
                embedding_model=embedding_model,
                embedding_dim=len(embedding),
                distance_metric=self.distance_metric,
                embedding=embedding,
                content_hash=content_hash,
                metadata=metadata,
                recency_score=recency_score,
            )
            .on_conflict_do_update(
                index_elements=[
                    Embedding.user_id,
                    Embedding.object_type,
                    Embedding.object_id,
                    Embedding.chunk_index,
                    Embedding.embedding_model,
                ],
                set_={
                    "embedding": embedding,
                    "content_hash": content_hash,
                    "metadata": metadata,
                    "recency_score": recency_score,
                    "updated_at": func.now(),
                },
            )
        )
        await session.execute(stmt)

    def _get_ranking_params(self, query_text: Optional[str]) -> Tuple[float, float]:
        """Adjust alpha/tau based on query intent."""
        alpha = settings.ranking_alpha
        tau_days = settings.ranking_tau_days

        if query_text:
            query_lower = query_text.lower()
            recency_keywords = ["latest", "recent", "today", "this week", "new", "now"]
            if any(kw in query_lower for kw in recency_keywords):
                # Boost recency: lower alpha or shorter tau
                alpha = 0.7  # Give more weight to recency
                tau_days = 7.0  # Shorter half-life

        return alpha, tau_days

    async def search(
        self,
        session: AsyncSession,
        *,
        user_id: str,
        query_embedding: Sequence[float],
        top_k: int = 20,
        object_types: Optional[List[str]] = None,
        time_start: Optional[datetime] = None,
        time_end: Optional[datetime] = None,
        sources: Optional[List[str]] = None,
        query_text: Optional[str] = None,
    ) -> List[VectorRecord]:
        """
        Semantic search using stored recency_score from embeddings.
        Hybrid ranking: semantic_score (from cosine distance) + recency_score (stored).
        """
        emb = Embedding

        # Stage A: Get topN candidates by semantic similarity
        query = (
            select(
                emb.id,
                emb.object_type,
                emb.object_id,
                emb.chunk_index,
                emb.meta,
                emb.recency_score,
                emb.embedding.cosine_distance(query_embedding).label("score"),
            )
            .where(emb.user_id == user_id)
            .order_by("score")
            .limit(settings.rerank_candidates_topn)
        )

        if object_types:
            query = query.where(emb.object_type.in_(object_types))

        # If filtering by time or sources, join to events when object_type == "event"
        need_event_filter = (time_start or time_end or sources) and (
            not object_types or "event" in object_types
        )
        if need_event_filter:
            evt = Event
            conditions = [emb.object_type == "event", emb.object_id == evt.id]
            if time_start:
                conditions.append(evt.occurred_at >= time_start)
            if time_end:
                conditions.append(evt.occurred_at <= time_end)
            if sources:
                conditions.append(evt.source.in_(sources))
            query = query.select_from(
                emb.__table__.join(evt.__table__, and_(*conditions))
            )

        rows = (await session.execute(query)).all()

        # Stage B: Rerank with hybrid scoring using stored recency_score
        alpha, _ = self._get_ranking_params(query_text)

        reranked = []
        for row in rows:
            # Convert distance to similarity [0, 1]
            sim = 1.0 - row.score
            # Use stored recency, default to 0.5 if not available
            recency = row.recency_score if row.recency_score is not None else 0.5

            # Calculate final score
            if settings.ranking_mode == "multiplier":
                final_score = sim * (0.5 + 0.5 * recency)
            else:  # weighted
                final_score = alpha * sim + (1 - alpha) * recency

            reranked.append(
                VectorRecord(
                    id=row.id,
                    object_type=row.object_type,
                    object_id=row.object_id,
                    chunk_index=row.chunk_index,
                    score=row.score,
                    metadata=row.meta or {},
                    recency_score=recency,
                    semantic_score=sim,
                    final_score=final_score,
                )
            )

        # Sort by final_score (desc), then semantic_score (desc)
        reranked.sort(
            key=lambda x: (x.final_score or 0, x.semantic_score or 0), reverse=True
        )
        return reranked[:top_k]

    async def delete_by_object(
        self,
        session: AsyncSession,
        *,
        user_id: str,
        object_type: str,
        object_id: str,
    ) -> int:
        """Delete embeddings for a specific object."""
        stmt = delete(Embedding).where(
            Embedding.user_id == user_id,
            Embedding.object_type == object_type,
            Embedding.object_id == object_id,
        )
        result = await session.execute(stmt)
        return result.rowcount or 0

    async def delete_by_user_time_range(
        self,
        session: AsyncSession,
        *,
        user_id: str,
        time_end: datetime,
        object_types: Optional[List[str]] = None,
    ) -> int:
        """Delete embeddings for events whose occurred_at is before time_end (used for retention)."""
        emb = Embedding
        evt_subq = (
            select(Event.id)
            .where(Event.user_id == user_id, Event.occurred_at < time_end)
            .correlate(None)
        )

        stmt = delete(Embedding).where(
            emb.user_id == user_id,
            emb.object_type == "event",
            emb.object_id.in_(evt_subq),
        )
        if object_types:
            stmt = stmt.where(emb.object_type.in_(object_types))

        stmt = stmt.execution_options(synchronize_session=False)
        result = await session.execute(stmt)
        return result.rowcount or 0


__all__ = ["VectorStore", "VectorRecord"]
