"""Tests for task schemas."""

from uuid import uuid4
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse


def test_task_create():
    """Test TaskCreate schema."""
    task = TaskCreate(
        status="open",
        priority="high",
        title="Follow up on email",
        details="Need to respond by Friday",
    )

    assert task.status == "open"
    assert task.priority == "high"
    assert task.title == "Follow up on email"


def test_task_update():
    """Test TaskUpdate schema."""
    task = TaskUpdate(status="done", priority="low")

    assert task.status == "done"
    assert task.priority == "low"


def test_task_response():
    """Test TaskResponse schema."""
    from datetime import datetime, timezone

    task = TaskResponse(
        id=uuid4(),
        user_id=uuid4(),
        status="open",
        priority="medium",
        title="Review document",
        details=None,
        due_at=None,
        source_event_id=None,
        source_refs=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    assert task.status == "open"
