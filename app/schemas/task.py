"""Task Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class TaskBase(BaseModel):
    """Base task schema."""

    status: str = "open"  # open | done | snoozed
    priority: str = "medium"  # low | medium | high
    title: str
    details: Optional[str] = None
    due_at: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Task creation schema."""

    source_event_id: Optional[UUID] = None
    source_refs: List[Dict[str, Any]] = []


class TaskUpdate(BaseModel):
    """Task update schema."""

    status: Optional[str] = None
    priority: Optional[str] = None
    title: Optional[str] = None
    details: Optional[str] = None
    due_at: Optional[datetime] = None


class TaskResponse(TaskBase):
    """Task response schema."""

    id: UUID
    user_id: UUID
    source_event_id: Optional[UUID] = None
    source_refs: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Task list response schema."""

    tasks: List[TaskResponse]
    total: int
    by_priority: Dict[str, int]
