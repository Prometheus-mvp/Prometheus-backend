"""Draft Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class DraftBase(BaseModel):
    """Base draft schema."""

    kind: str  # slack_reply | telegram_reply | outlook_reply | note
    content_json: Dict[str, Any]
    source_refs: List[Dict[str, Any]] = []


class DraftCreate(DraftBase):
    """Draft creation schema."""

    pass


class DraftUpdate(BaseModel):
    """Draft update schema."""

    kind: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    source_refs: Optional[List[Dict[str, Any]]] = None


class DraftResponse(DraftBase):
    """Draft response schema."""

    id: UUID
    user_id: UUID
    content_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

