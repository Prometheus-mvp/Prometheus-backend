"""Thread Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class ThreadBase(BaseModel):
    """Base thread schema."""

    source: str  # slack | telegram | outlook
    external_id: str
    subject: Optional[str] = None
    participants: List[Dict[str, Any]] = []
    content_preview: Optional[str] = None


class ThreadCreate(ThreadBase):
    """Thread creation schema."""

    pass


class ThreadUpdate(BaseModel):
    """Thread update schema."""

    subject: Optional[str] = None
    participants: Optional[List[Dict[str, Any]]] = None
    content_preview: Optional[str] = None
    last_event_at: Optional[datetime] = None


class ThreadResponse(ThreadBase):
    """Thread response schema."""

    id: UUID
    user_id: UUID
    content_hash: str
    last_event_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


