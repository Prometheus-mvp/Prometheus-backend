"""Tests for Event model."""
import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from app.models.event import Event


def test_event_creation():
    """Test Event model can be instantiated."""
    user_id = uuid4()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=30)
    
    event = Event(
        user_id=user_id,
        source="slack",
        external_id="msg_123",
        event_type="message",
        title="Test Message",
        body="Hello world",
        occurred_at=now,
        expires_at=expires
    )
    
    assert event.user_id == user_id
    assert event.source == "slack"
    assert event.external_id == "msg_123"
    assert event.event_type == "message"
    assert event.title == "Test Message"
    assert event.body == "Hello world"


def test_event_with_thread():
    """Test Event with thread_id."""
    user_id = uuid4()
    thread_id = uuid4()
    now = datetime.now(timezone.utc)
    
    event = Event(
        user_id=user_id,
        source="telegram",
        external_id="msg_456",
        thread_id=thread_id,
        event_type="message",
        occurred_at=now,
        expires_at=now + timedelta(days=30)
    )
    
    assert event.thread_id == thread_id

