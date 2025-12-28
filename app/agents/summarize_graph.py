"""Summarize agent workflow."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentBase
from app.models import Summary
from app.services.embedding import EmbeddingService
from app.services.vector import VectorStore


class SummarizeAgent(AgentBase):
    """Agent that summarizes recent events."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        super().__init__()
        self.vector_store = vector_store or VectorStore()
        self.embedding_service = embedding_service or EmbeddingService(
            vector_store=self.vector_store
        )

    async def summarize(
        self,
        session: AsyncSession,
        *,
        user_id: str,
        prompt: str,
        hours: int = 2,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Summarize last N hours of events using vector search as retrieval."""
        time_end = datetime.now(timezone.utc)
        time_start = time_end - timedelta(hours=hours)
        # Retrieve top events by semantic search (prompt as query)
        query_vector = (await self.embedding_service.embed_text([prompt]))[0]
        vector_results = await self.vector_store.search(
            session,
            user_id=user_id,
            query_embedding=query_vector,
            top_k=50,
            object_types=["event"],
            time_start=time_start,
            time_end=time_end,
            sources=sources,
        )

        # Build a simple context text
        context_lines = []
        for vr in vector_results:
            context_lines.append(f"- [{vr.object_type}:{vr.object_id}] {vr.metadata}")
        context = "\n".join(context_lines)

        llm_prompt = (
            "Summarize the following user activity over the time window. "
            "Return JSON with keys: overview (string), key_events (list), "
            "themes (list). "
            f"User prompt: {prompt}\n"
            f"Context:\n{context}"
        )
        result = await self.complete_json(
            llm_prompt,
            schema={
                "overview": "string",
                "key_events": "array",
                "themes": "array",
            },
        )

        summary = Summary(
            user_id=user_id,
            window_start=time_start,
            window_end=time_end,
            content_json=result,
            source_refs=[
                {"object_id": vr.object_id, "object_type": vr.object_type}
                for vr in vector_results
            ],
        )
        session.add(summary)
        return result


summarize_agent = SummarizeAgent()

__all__ = ["SummarizeAgent", "summarize_agent"]

