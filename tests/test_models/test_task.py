"""Tests for Task model."""

from uuid import uuid4
from app.models.task import Task


def test_task_creation():
    """Test Task model can be instantiated."""
    user_id = uuid4()
    task = Task(
        user_id=user_id, status="open", priority="high", title="Follow up on email"
    )

    assert task.user_id == user_id
    assert task.status == "open"
    assert task.priority == "high"
    assert task.title == "Follow up on email"


def test_task_with_source_event():
    """Test Task with source_event_id."""
    user_id = uuid4()
    event_id = uuid4()

    task = Task(
        user_id=user_id,
        status="open",
        priority="medium",
        title="Review document",
        source_event_id=event_id,
    )

    assert task.source_event_id == event_id
