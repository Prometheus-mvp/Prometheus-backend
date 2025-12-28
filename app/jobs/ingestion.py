"""Event ingestion job (poll connectors every 5 minutes)."""
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, LinkedAccount
from app.services.connector import (
    outlook_connector,
    slack_connector,
    telegram_connector,
)

logger = logging.getLogger(__name__)


async def ingest_events_for_user(session: AsyncSession, user_id: str) -> int:
    """
    Ingest events for a single user from all connectors with idempotency.
    """
    total = 0
    connectors = [slack_connector, telegram_connector, outlook_connector]
    now = datetime.now(timezone.utc)

    # Fetch linked accounts for the user to limit providers
    result = await session.execute(
        select(LinkedAccount).where(LinkedAccount.user_id == user_id)
    )
    accounts = result.scalars().all()
    provider_map = {acc.provider: acc for acc in accounts}

    for connector in connectors:
        if connector.provider not in provider_map:
            continue
        try:
            events = await connector.fetch_events(
                session=session, user_id=user_id, since=None
            )
        except Exception as exc:
            logger.warning(
                "Connector fetch failed",
                extra={"provider": connector.provider, "error": str(exc)},
            )
            continue
        for evt in events:
            stmt = (
                insert(Event)
                .values(
                    user_id=user_id,
                    source=evt.get("source", connector.provider),
                    source_account_id=evt.get("source_account_id"),
                    external_id=evt.get("external_id"),
                    thread_id=evt.get("thread_id"),
                    event_type=evt.get("event_type", "message"),
                    title=evt.get("title"),
                    body=evt.get("body"),
                    url=evt.get("url"),
                    text_for_embedding=evt.get("text_for_embedding"),
                    content_hash=evt.get("content_hash", ""),
                    importance_score=evt.get("importance_score", 0),
                    occurred_at=evt.get("occurred_at", now),
                    expires_at=evt.get(
                        "expires_at", now + timedelta(days=30)
                    ),
                    deleted_at=None,
                    raw=evt.get("raw", {}),
                )
                .on_conflict_do_nothing(
                    index_elements=["user_id", "source", "external_id"]
                )
            )
            result = await session.execute(stmt)
            if result.rowcount and result.rowcount > 0:
                total += 1

    logger.info("Ingestion completed", extra={"user_id": user_id, "count": total})
    return total

