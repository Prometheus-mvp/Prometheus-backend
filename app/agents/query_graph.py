"""Push-based Query Agent - Context Bank for all agents.

This agent is push-based: it runs on schedule/events via background job
to proactively build and maintain the context bank.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentBase
from app.services.embedding import EmbeddingService
from app.services.vector import VectorStore

if TYPE_CHECKING:
    from app.agents.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)


class QueryAgent(AgentBase):
    """
    Push-based agent that acts as context bank for all other agents.

    Runs on schedule/events to proactively build context by:
    - Fetching events via connector APIs
    - Generating embeddings with recency scores
    - Storing context in context bank
    - Providing fine-grained search capabilities
    - Can call SummarizeAgent to broaden context for specific time frames
    """

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
        orchestrator: Optional["AgentOrchestrator"] = None,
    ) -> None:
        super().__init__(orchestrator=orchestrator)
        self.vector_store = vector_store or VectorStore()
        self.embedding_service = embedding_service or EmbeddingService(
            vector_store=self.vector_store
        )

    async def build_context_bank(
        self,
        session: AsyncSession,
        *,
        user_id: str,
        time_window_hours: int = 24,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Push-based method: Proactively build context bank by fetching events,
        generating embeddings with recency scores, and storing context.

        Called by background job at intervals or on events.
        """
        from app.jobs.ingestion import ingest_events_for_user

        # Fetch new events via connectors and generate embeddings
        event_count = await ingest_events_for_user(session, user_id)

        logger.info(
            "Context bank updated",
            extra={
                "user_id": user_id,
                "events_processed": event_count,
                "sources": sources or ["all"],
            },
        )

        return {
            "events_processed": event_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sources": sources or ["slack", "telegram", "outlook"],
        }

    async def fine_grained_search(
        self,
        session: AsyncSession,
        *,
        user_id: str,
        query: str,
        sources: Optional[List[str]] = None,
        time_start: Optional[datetime] = None,
        time_end: Optional[datetime] = None,
        top_k: int = 20,
    ) -> Dict[str, Any]:
        """
        Fine-grained search using semantic similarity + stored recency scores.

        Used by other agents to retrieve specific context from the context bank.
        Returns results ranked by combined semantic + recency score.
        """
        query_vector = (await self.embedding_service.embed_text([query]))[0]
        vector_results = await self.vector_store.search(
            session,
            user_id=user_id,
            query_embedding=query_vector,
            top_k=top_k,
            object_types=["event"],
            time_start=time_start,
            time_end=time_end,
            sources=sources,
            query_text=query,
        )

        return {
            "results": [
                {
                    "object_id": str(vr.object_id),
                    "object_type": vr.object_type,
                    "semantic_score": vr.semantic_score,
                    "recency_score": vr.recency_score,
                    "final_score": vr.final_score,
                    "metadata": vr.metadata,
                }
                for vr in vector_results
            ],
            "query": query,
            "result_count": len(vector_results),
        }

    async def answer_query_with_context(
        self,
        session: AsyncSession,
        *,
        user_id: str,
        prompt: str,
        sources: List[str],
        time_start: datetime,
        time_end: datetime,
    ) -> Dict[str, Any]:
        """
        Answer user query using context bank.

        Can call SummarizeAgent to broaden context if:
        - Search results have low recency scores (old context)
        - Additional summarization needed for specific time frames
        """
        # Fine-grained search from context bank
        search_results = await self.fine_grained_search(
            session,
            user_id=user_id,
            query=prompt,
            sources=sources,
            time_start=time_start,
            time_end=time_end,
        )

        # Check if we need broader context based on recency scores
        results = search_results.get("results", [])
        broader_context = None

        if results:
            avg_recency = sum(r["recency_score"] or 0.5 for r in results) / len(results)
            if avg_recency < 0.3 and self.orchestrator:
                # Old context - try to get summary for broader context
                summary_result = await self.orchestrator.get_agent_result(
                    "summarize", time_window_hours=24
                )
                if summary_result:
                    broader_context = summary_result.get("overview", "")

        # Build answer using search results
        context_lines = []
        for r in results[:10]:
            score_info = f"Score: {r['final_score']:.3f}"
            if r["semantic_score"] is not None and r["recency_score"] is not None:
                score_info += (
                    f" (sem: {r['semantic_score']:.3f}, rec: {r['recency_score']:.3f})"
                )
            context_lines.append(f"- [{r['object_id']}] {score_info}")

        context = "\n".join(context_lines)

        # Build LLM prompt
        llm_prompt_parts = [
            "Answer the user's question using the following context from the context bank.",
            "",
        ]

        if broader_context:
            llm_prompt_parts.append(f"Broader context from summary:\n{broader_context}")
            llm_prompt_parts.append("")

        llm_prompt_parts.extend(
            [
                f"Relevant context:\n{context}",
                "",
                f"User question: {prompt}",
                "",
                "Return JSON with: answer (string), confidence (float 0-1), citations (list of object_ids).",
            ]
        )

        llm_prompt = "\n".join(llm_prompt_parts)

        result = await self.complete_json(
            llm_prompt,
            schema={
                "answer": "string",
                "confidence": "number",
                "citations": "array",
            },
        )

        return result


# Module-level singleton for convenience
query_agent = QueryAgent()

__all__ = ["QueryAgent", "query_agent"]
