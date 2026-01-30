"""Embedding generation job."""

import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.embedding import (
    EmbeddingObject,
    EmbeddingService,
    compute_content_hash,
)

logger = logging.getLogger(__name__)


async def embed_objects(
    session: AsyncSession,
    objects: List[EmbeddingObject],
    embedding_service: EmbeddingService,
) -> int:
    """
    Generate embeddings for provided objects.

    Caller is responsible for selecting objects needing embedding and supplying
    content_hash (or it will be computed).
    """
    if not objects:
        return 0
    # Ensure content_hash present for idempotency
    for obj in objects:
        if not obj.content_hash:
            obj.content_hash = compute_content_hash(obj.text or "")

    count = await embedding_service.embed_and_store(session, objects)
    logger.info("Embedding job processed objects", extra={"count": count})
    return count


__all__ = ["embed_objects"]
