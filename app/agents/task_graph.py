"""Task detection agent workflow."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentBase
from app.models import Task
from app.services.embedding import EmbeddingService
from app.services.vector import VectorStore


class TaskAgent(AgentBase):
    """Agent that detects actionable tasks."""

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

    async def detect_tasks(
        self,
        session: AsyncSession,
        *,
        user_id: str,
        prompt: str,
        sources: Optional[List[str]] = None,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """Identify tasks from recent events."""
        time_end = datetime.now(timezone.utc)
        time_start = time_end - timedelta(hours=hours)

        # Retrieve top events
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

        context_lines = []
        for vr in vector_results:
            context_lines.append(f"- [{vr.object_type}:{vr.object_id}] {vr.metadata}")
        context = "\n".join(context_lines)

        llm_prompt = (
            "Identify actionable tasks from the following context. "
            "Return JSON with tasks: list of {title, details, priority, "
            "due_at|null, source_refs:list}."
            f"User prompt: {prompt}\nContext:\n{context}"
        )
        result = await self.complete_json(
            llm_prompt,
            schema={
                "tasks": "array",
            },
        )

        # Persist tasks
        tasks_out = []
        for t in result.get("tasks", []):
            task_obj = Task(
                user_id=user_id,
                status="open",
                priority=t.get("priority", "medium"),
                title=t.get("title", "Untitled task"),
                details=t.get("details"),
                due_at=t.get("due_at"),
                source_event_id=None,
                source_refs=t.get("source_refs", []),
            )
            session.add(task_obj)
            tasks_out.append(task_obj)

        return {"tasks": result.get("tasks", [])}


task_agent = TaskAgent()

__all__ = ["TaskAgent", "task_agent"]
