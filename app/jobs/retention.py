"""Retention cleanup job."""
import logging
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event
from app.services.vector import VectorStore

logger = logging.getLogger(__name__)


async def run_retention(
    session: AsyncSession,
    *,
    user_id: str,
    now: datetime | None = None,
    batch_size: int = 1000,
) -> dict:
    """Delete expired events and related embeddings/summaries/proposals."""
    now = now or datetime.now(timezone.utc)
    vector_store = VectorStore()

    # Delete events expired
    delete_events_stmt = (
        delete(Event)
        .where(Event.user_id == user_id, Event.expires_at < now)
        .returning(Event.id)
    )
    result = await session.execute(delete_events_stmt)
    deleted_event_ids = [row[0] for row in result.fetchall()]

    # Delete embeddings for deleted events
    deleted_embeddings = 0
    for evt_id in deleted_event_ids:
        deleted_embeddings += await vector_store.delete_by_object(
            session,
            user_id=user_id,
            object_type="event",
            object_id=str(evt_id),
        )

    # Delete expired summaries/proposals (if any date-based policy)
    # Here, assume summaries are retained; if needed add window_end < now - 30d
    # Delete orphaned embeddings by time window
    deleted_embeddings += await vector_store.delete_by_user_time_range(
        session, user_id=user_id, time_end=now
    )

    logger.info(
        "Retention job completed",
        extra={
            "user_id": user_id,
            "deleted_events": len(deleted_event_ids),
            "deleted_embeddings": deleted_embeddings,
        },
    )
    return {
        "deleted_events": len(deleted_event_ids),
        "deleted_embeddings": deleted_embeddings,
    }


__all__ = ["run_retention"]

