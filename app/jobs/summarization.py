"""Summarization job to generate summaries and proposals."""
import logging
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.summarize_graph import summarize_agent

logger = logging.getLogger(__name__)


async def run_summarization(
    session: AsyncSession,
    *,
    user_id: str,
    hours: int = 2,
    sources: Optional[List[str]] = None,
) -> dict:
    """Generate summary and proposals for a time window."""
    result = await summarize_agent.summarize(
        session, user_id=user_id, prompt="summarize", hours=hours, sources=sources
    )
    logger.info("Summarization job completed", extra={"user_id": user_id})
    return result


__all__ = ["run_summarization"]

