"""Tests for tasks API endpoints."""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_tasks_success():
    """Test listing tasks successfully."""
    from app.api.v1.tasks import list_tasks

    user_id = str(uuid4())
    mock_db = AsyncMock()
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await list_tasks(db=mock_db, user_id=user_id)

    assert response.total == 0
    assert response.tasks == []
    assert response.by_priority == {"low": 0, "medium": 0, "high": 0}


@pytest.mark.asyncio
async def test_list_tasks_with_filters():
    """Test listing tasks with status filter."""
    from app.api.v1.tasks import list_tasks

    user_id = str(uuid4())
    mock_db = AsyncMock()
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await list_tasks(
        db=mock_db, user_id=user_id, status="open", priority="high"
    )

    assert response.total == 0
    mock_db.execute.assert_called_once()
