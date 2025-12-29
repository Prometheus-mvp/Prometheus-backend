"""Tests for retention cleanup job."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_cleanup_expired_events_no_expired():
    """Test cleanup when no events are expired."""
    from app.jobs.retention import cleanup_expired_events

    mock_db = AsyncMock()
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    deleted_count = await cleanup_expired_events(mock_db)

    assert deleted_count == 0


@pytest.mark.asyncio
async def test_cleanup_expired_events_with_expired():
    """Test cleanup with expired events."""
    from app.jobs.retention import cleanup_expired_events
    from app.models.event import Event
    from uuid import uuid4
    from datetime import timedelta

    # Mock expired events
    past = datetime.now(timezone.utc) - timedelta(days=31)
    event1 = Event(
        id=uuid4(),
        user_id=uuid4(),
        source="slack",
        external_id="msg1",
        event_type="message",
        occurred_at=past,
        expires_at=past,
    )

    mock_db = AsyncMock()
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = [event1]
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch("app.jobs.retention.VectorStore") as mock_vs:
        mock_vs_instance = Mock()
        mock_vs_instance.delete_by_object = AsyncMock()
        mock_vs.return_value = mock_vs_instance

        deleted_count = await cleanup_expired_events(mock_db, batch_size=100)

        assert deleted_count > 0
        mock_vs_instance.delete_by_object.assert_called()
