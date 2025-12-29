"""Summary Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from pydantic import BaseModel


class SummaryBase(BaseModel):
    """Base summary schema."""

    window_start: datetime
    window_end: datetime
    content_json: Dict[str, Any]
    source_refs: List[Dict[str, Any]] = []


class SummaryCreate(SummaryBase):
    """Summary creation schema."""

    pass


class SummaryResponse(SummaryBase):
    """Summary response schema."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
