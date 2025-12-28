"""Event Pydantic schemas."""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class EventBase(BaseModel):
    """Base event schema."""
    source: str
    external_id: str
    event_type: str
    title: Optional[str] = None
    body: Optional[str] = None
    url: Optional[str] = None
    occurred_at: datetime


class EventCreate(EventBase):
    """Event creation schema."""
    source_account_id: Optional[UUID] = None
    thread_id: Optional[UUID] = None
    text_for_embedding: Optional[str] = None
    importance_score: int = 0
    expires_at: datetime
    raw: Dict[str, Any] = {}


class EventResponse(EventBase):
    """Event response schema."""
    id: UUID
    user_id: UUID
    source_account_id: Optional[UUID] = None
    thread_id: Optional[UUID] = None
    text_for_embedding: Optional[str] = None
    content_hash: str
    importance_score: int
    expires_at: datetime
    deleted_at: Optional[datetime] = None
    raw: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

