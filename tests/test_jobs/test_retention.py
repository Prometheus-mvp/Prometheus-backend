"""Tests for retention cleanup job."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4


@pytest.mark.asyncio
async def test_cleanup_expired_events_no_expired():
    """Test run_retention when no events are expired."""
    from app.jobs.retention import run_retention

    user_id = str(uuid4())
    mock_db = AsyncMock()
    mock_delete_result = Mock()
    mock_delete_result.fetchall.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_delete_result)

    with patch("app.jobs.retention.VectorStore") as mock_vs:
        mock_vs_instance = Mock()
        mock_vs_instance.delete_by_object = AsyncMock(return_value=0)
        mock_vs_instance.delete_by_user_time_range = AsyncMock(return_value=0)
        mock_vs.return_value = mock_vs_instance

        result = await run_retention(mock_db, user_id=user_id)

    assert result["deleted_events"] == 0
    assert "deleted_embeddings" in result


@pytest.mark.asyncio
async def test_cleanup_expired_events_with_expired():
    """Test run_retention with expired events."""
    from app.jobs.retention import run_retention

    user_id = str(uuid4())
    deleted_event_id = uuid4()
    mock_db = AsyncMock()
    mock_delete_result = Mock()
    mock_delete_result.fetchall.return_value = [(deleted_event_id,)]
    mock_db.execute = AsyncMock(return_value=mock_delete_result)

    with patch("app.jobs.retention.VectorStore") as mock_vs:
        mock_vs_instance = Mock()
        mock_vs_instance.delete_by_object = AsyncMock(return_value=1)
        mock_vs_instance.delete_by_user_time_range = AsyncMock(return_value=0)
        mock_vs.return_value = mock_vs_instance

        result = await run_retention(mock_db, user_id=user_id, batch_size=100)

    assert result["deleted_events"] == 1
    mock_vs_instance.delete_by_object.assert_called()
    mock_vs_instance.delete_by_user_time_range.assert_called_once()
