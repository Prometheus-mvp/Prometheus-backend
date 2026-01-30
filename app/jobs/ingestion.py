"""Event ingestion job (poll connectors every 5 minutes)."""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, LinkedAccount
from app.services.connector import (
    outlook_connector,
    slack_connector,
    telegram_connector,
)
from app.services.embedding import EmbeddingObject, EmbeddingService

logger = logging.getLogger(__name__)


async def ingest_events_for_user(session: AsyncSession, user_id: str) -> int:
    """
    Ingest events for a single user from all connectors with idempotency.
    Messages are not stored - only used for generating embeddings.
    """
    total = 0
    connectors = [slack_connector, telegram_connector, outlook_connector]
    now = datetime.now(timezone.utc)

    # Collect embedding objects to process after event insertion
    embedding_objects: List[Tuple[EmbeddingObject, datetime]] = []

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
            # Extract embedding text (not stored in event)
            embedding_text = evt.pop("_embedding_text", None)
            occurred_at = evt.get("occurred_at", now)

            # Store event without message content
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
                    # Note: body and text_for_embedding removed - messages not stored
                    url=evt.get("url"),
                    content_hash=evt.get("content_hash", ""),
                    importance_score=evt.get("importance_score", 0),
                    occurred_at=occurred_at,
                    expires_at=evt.get("expires_at", now + timedelta(days=30)),
                    deleted_at=None,
                    raw=evt.get("raw", {}),
                )
                .on_conflict_do_nothing(
                    index_elements=["user_id", "source", "external_id"]
                )
                .returning(Event.id)
            )
            result = await session.execute(stmt)
            row = result.fetchone()

            if row:
                event_id = row[0]
                total += 1

                # Queue embedding generation if text available
                if embedding_text and embedding_text.strip():
                    embedding_objects.append(
                        (
                            EmbeddingObject(
                                user_id=user_id,
                                object_type="event",
                                object_id=str(event_id),
                                text=embedding_text,
                                metadata={
                                    "source": evt.get("source", connector.provider)
                                },
                                occurred_at=occurred_at,
                            ),
                            occurred_at,
                        )
                    )

    # Generate embeddings for all new events (with recency scores)
    if embedding_objects:
        embedding_service = EmbeddingService()
        try:
            # Extract just the EmbeddingObjects
            objects_to_embed = [obj for obj, _ in embedding_objects]
            await embedding_service.embed_and_store(session, objects_to_embed)
        except Exception as exc:
            logger.warning(
                "Embedding generation failed",
                extra={"user_id": user_id, "error": str(exc)},
            )

    logger.info("Ingestion completed", extra={"user_id": user_id, "count": total})
    return total
