"""Calendar Pydantic schemas."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class CalendarEventBase(BaseModel):
    """Base calendar event schema."""
    title: str
    description: Optional[str] = None
    start_at: datetime
    end_at: datetime
    location: Optional[str] = None


class CalendarEventCreate(CalendarEventBase):
    """Calendar event creation schema."""
    pass


class CalendarEventUpdate(BaseModel):
    """Calendar event update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    location: Optional[str] = None


class CalendarEventResponse(CalendarEventBase):
    """Calendar event response schema."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CalendarEventListResponse(BaseModel):
    """Calendar event list response schema."""
    events: List[CalendarEventResponse]
    total: int

