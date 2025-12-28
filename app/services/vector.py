"""VectorStore abstraction (pgvector implementation)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Embedding, Event


@dataclass
class VectorRecord:
    """Returned vector search record."""

    id: str
    object_type: str
    object_id: str
    chunk_index: int
    score: float
    metadata: Dict[str, Any]


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
    ) -> None:
        """Upsert an embedding row."""
        metadata = metadata or {}
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
                    "updated_at": func.now(),
                },
            )
        )
        await session.execute(stmt)

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
    ) -> List[VectorRecord]:
        """Semantic search with optional filters (time window and sources for events)."""
        emb = Embedding
        query = (
            select(
                emb.id,
                emb.object_type,
                emb.object_id,
                emb.chunk_index,
                emb.metadata,
                emb.embedding.cosine_distance(query_embedding).label("score"),
            )
            .where(emb.user_id == user_id)
            .order_by("score")
            .limit(top_k)
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
            query = (
                query.select_from(emb.__table__.join(evt.__table__, and_(*conditions)))
            )

        rows = (await session.execute(query)).all()
        return [
            VectorRecord(
                id=row.id,
                object_type=row.object_type,
                object_id=row.object_id,
                chunk_index=row.chunk_index,
                score=row.score,
                metadata=row.metadata or {},
            )
            for row in rows
        ]

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
        evt = Event
        stmt = (
            delete(Embedding)
            .where(
                emb.user_id == user_id,
                emb.object_type == "event",
                emb.object_id == evt.id,
                evt.occurred_at < time_end,
            )
            .where(True)
            .execution_options(synchronize_session=False)
        )
        if object_types:
            stmt = stmt.where(emb.object_type.in_(object_types))
        result = await session.execute(stmt)
        return result.rowcount or 0


__all__ = ["VectorStore", "VectorRecord"]

