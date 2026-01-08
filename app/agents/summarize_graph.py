"""Summarize agent workflow - Pull-based agent.

This agent is pull-based: it only executes when user explicitly requests a summary.
Can call QueryAgent to get context outside the prompt scope.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentBase
from app.models import Summary
from app.services.embedding import EmbeddingService
from app.services.vector import VectorStore

if TYPE_CHECKING:
    from app.agents.orchestrator import AgentOrchestrator


class SummarizeAgent(AgentBase):
    """
    Pull-based agent: Only executes when user explicitly requests summary.
    
    Can call QueryAgent to get context outside prompt scope for
    more comprehensive summaries.
    """

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
        orchestrator: Optional["AgentOrchestrator"] = None,
    ):
        super().__init__(orchestrator=orchestrator)
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
        time_start: datetime,
        time_end: datetime,
        sources: List[str],
    ) -> Dict[str, Any]:
        """
        Summarize events in the specified time range - only called on user request (pull-based).
        
        Uses stored recency scores in hybrid ranking.
        Can use QueryAgent's context bank for additional context.
        """
        # Optionally get additional context from QueryAgent
        query_context = None
        if self.orchestrator:
            from app.agents.query_graph import QueryAgent

            query_agent = QueryAgent(orchestrator=self.orchestrator)
            try:
                query_context = await query_agent.fine_grained_search(
                    session,
                    user_id=user_id,
                    query=prompt,
                    sources=sources,
                    time_start=time_start,
                    time_end=time_end,
                    top_k=10,
                )
            except Exception as exc:
                self.logger.warning(
                    "Failed to get QueryAgent context",
                    extra={"error": str(exc)},
                )

        # Retrieve events by semantic search (uses stored recency_score)
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
            query_text=prompt,
        )

        # Build context (no message content, only metadata from embeddings)
        context_lines = []
        for vr in vector_results:
            score_info = f"Score: {vr.final_score:.3f}" if vr.final_score else ""
            if vr.semantic_score is not None and vr.recency_score is not None:
                score_info += f" (sem: {vr.semantic_score:.3f}, rec: {vr.recency_score:.3f})"
            context_lines.append(
                f"- [{vr.object_type}:{vr.object_id}] {score_info} Metadata: {vr.metadata}"
            )
        context = "\n".join(context_lines)

        # Include QueryAgent context if available
        extra_context = ""
        if query_context and query_context.get("results"):
            extra_context = (
                f"\nAdditional fine-grained context ({query_context.get('result_count', 0)} items):\n"
                + "\n".join(
                    f"- {r['object_id']}: score {r.get('final_score', 0):.3f}"
                    for r in query_context["results"][:5]
                )
            )

        llm_prompt = (
            "Summarize the following user activity over the time window. "
            "Return JSON with keys: overview (string), key_events (list), "
            "themes (list). "
            f"User prompt: {prompt}\n"
            f"Context:\n{context}"
            f"{extra_context}"
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
                {"object_id": str(vr.object_id), "object_type": vr.object_type}
                for vr in vector_results
            ],
        )
        session.add(summary)
        return result


summarize_agent = SummarizeAgent()

__all__ = ["SummarizeAgent", "summarize_agent"]
