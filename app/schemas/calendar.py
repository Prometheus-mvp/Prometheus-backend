"""Calendar Pydantic schemas."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class CalendarEventBase(BaseModel):
    """Base calendar event schema."""

    title: str = Field(..., min_length=1, max_length=500, description="Event title")
    description: Optional[str] = Field(
        None, max_length=5000, description="Event description"
    )
    start_at: datetime = Field(
        ..., description="Event start date and time (timezone-aware)"
    )
    end_at: datetime = Field(
        ..., description="Event end date and time (timezone-aware)"
    )
    location: Optional[str] = Field(None, max_length=500, description="Event location")

    @model_validator(mode="after")
    def validate_date_range(self) -> "CalendarEventBase":
        """Validate that end_at is after start_at."""
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        return self


class CalendarEventCreate(CalendarEventBase):
    """Calendar event creation schema."""

    pass


class CalendarEventUpdate(BaseModel):
    """Calendar event update schema."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=500, description="Event title"
    )
    description: Optional[str] = Field(
        None, max_length=5000, description="Event description"
    )
    start_at: Optional[datetime] = Field(
        None, description="Event start date and time (timezone-aware)"
    )
    end_at: Optional[datetime] = Field(
        None, description="Event end date and time (timezone-aware)"
    )
    location: Optional[str] = Field(None, max_length=500, description="Event location")

    @model_validator(mode="after")
    def validate_date_range(self) -> "CalendarEventUpdate":
        """Validate that end_at is after start_at if both are provided."""
        if self.start_at is not None and self.end_at is not None:
            if self.end_at <= self.start_at:
                raise ValueError("end_at must be after start_at")
        return self


class CalendarEventResponse(CalendarEventBase):
    """Calendar event response schema."""

    id: UUID = Field(..., description="Unique event identifier")
    user_id: UUID = Field(..., description="User who owns this event")
    created_at: datetime = Field(..., description="Event creation timestamp")
    updated_at: datetime = Field(..., description="Event last update timestamp")

    class Config:
        from_attributes = True


class CalendarEventListResponse(BaseModel):
    """Calendar event list response schema."""

    events: List[CalendarEventResponse] = Field(
        ..., description="List of calendar events"
    )
    total: int = Field(..., description="Total number of events")
