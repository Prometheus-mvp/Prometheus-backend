"""Background job for push-based QueryAgent execution.

This job runs at intervals to proactively build the context bank
by fetching events and generating embeddings with recency scores.
"""

import logging
from typing import Any, Dict

from app.agents.query_graph import QueryAgent
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def run_query_agent_context_bank(user_id: str) -> Dict[str, Any]:
    """
    Background job to run push-based QueryAgent.
    
    Called at intervals (e.g., every hour) or on events (new events ingested).
    Builds the context bank by fetching events and generating embeddings.
    """
    async with AsyncSessionLocal() as session:
        query_agent = QueryAgent()
        result = await query_agent.build_context_bank(
            session,
            user_id=user_id,
            time_window_hours=24,
        )
        await session.commit()

        logger.info(
            "Query agent context bank job completed",
            extra={
                "user_id": user_id,
                "events_processed": result.get("events_processed", 0),
            },
        )

        return result


async def run_query_agent_for_all_users() -> Dict[str, Any]:
    """
    Background job to run QueryAgent for all active users.
    
    Scheduled to run periodically (e.g., every hour) to keep
    all users' context banks up to date.
    """
    from sqlalchemy import select

    from app.models import User

    results = {}

    async with AsyncSessionLocal() as session:
        # Get all users
        query = select(User.id)
        result = await session.execute(query)
        user_ids = [str(row[0]) for row in result.fetchall()]

    for user_id in user_ids:
        try:
            user_result = await run_query_agent_context_bank(user_id)
            results[user_id] = {
                "status": "success",
                "events_processed": user_result.get("events_processed", 0),
            }
        except Exception as exc:
            logger.error(
                "Query agent failed for user",
                extra={"user_id": user_id, "error": str(exc)},
            )
            results[user_id] = {
                "status": "error",
                "error": str(exc),
            }

    logger.info(
        "Query agent batch job completed",
        extra={"users_processed": len(results)},
    )

    return results


__all__ = ["run_query_agent_context_bank", "run_query_agent_for_all_users"]

