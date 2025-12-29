"""Tests for calendar API endpoints."""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from datetime import datetime, timezone, timedelta


@pytest.mark.asyncio
async def test_list_calendar_events():
    """Test listing calendar events."""
    from app.api.v1.calendar import list_calendar_events

    user_id = str(uuid4())
    mock_db = AsyncMock()
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await list_calendar_events(db=mock_db, user_id=user_id)

    assert response.total == 0
    assert response.events == []


@pytest.mark.asyncio
async def test_create_calendar_event():
    """Test creating a calendar event."""
    from app.api.v1.calendar import create_calendar_event
    from app.schemas.calendar import CalendarEventCreate

    user_id = str(uuid4())
    mock_db = AsyncMock()

    event_data = CalendarEventCreate(
        title="Team Meeting",
        description="Weekly sync",
        start_at=datetime.now(timezone.utc),
        end_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    response = await create_calendar_event(
        event=event_data, db=mock_db, user_id=user_id
    )

    assert response.title == "Team Meeting"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_calendar_event_not_found():
    """Test deleting calendar event that doesn't exist."""
    from app.api.v1.calendar import delete_calendar_event
    from fastapi import HTTPException

    user_id = str(uuid4())
    event_id = uuid4()
    mock_db = AsyncMock()
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc_info:
        await delete_calendar_event(event_id=event_id, db=mock_db, user_id=user_id)

    assert exc_info.value.status_code == 404
