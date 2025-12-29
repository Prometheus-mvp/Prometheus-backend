"""Tests for embedding job."""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4


@pytest.mark.asyncio
async def test_embed_objects_empty_list():
    """Test embed_objects with empty list."""
    from app.jobs.embedding import embed_objects

    mock_db = AsyncMock()
    mock_service = Mock()
    mock_service.embed_and_store = AsyncMock()

    await embed_objects(mock_db, [], mock_service)

    # Should not call embed_and_store
    mock_service.embed_and_store.assert_not_called()


@pytest.mark.asyncio
async def test_embed_objects_success():
    """Test embed_objects with objects."""
    from app.jobs.embedding import embed_objects
    from app.services.embedding import EmbeddingObject

    mock_db = AsyncMock()
    mock_service = Mock()
    mock_service.embed_and_store = AsyncMock()

    objects = [
        EmbeddingObject(
            user_id=str(uuid4()),
            object_type="event",
            object_id=uuid4(),
            text="Test event",
            chunk_index=0,
        )
    ]

    await embed_objects(mock_db, objects, mock_service)

    mock_service.embed_and_store.assert_called_once_with(mock_db, objects)
