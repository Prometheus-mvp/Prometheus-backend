"""Note Pydantic schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class NoteBase(BaseModel):
    """Base note schema."""

    title: Optional[str] = None
    body: str


class NoteCreate(NoteBase):
    """Note creation schema."""

    pass


class NoteUpdate(BaseModel):
    """Note update schema."""

    title: Optional[str] = None
    body: Optional[str] = None


class NoteResponse(NoteBase):
    """Note response schema."""

    id: UUID
    user_id: UUID
    content_hash: str
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
