"""Proposal Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class ProposalBase(BaseModel):
    """Base proposal schema."""

    window_start: datetime
    window_end: datetime
    content_json: Dict[str, Any]
    source_refs: List[Dict[str, Any]] = []


class ProposalCreate(ProposalBase):
    """Proposal creation schema."""

    pass


class ProposalUpdate(BaseModel):
    """Proposal update schema."""

    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None
    content_json: Optional[Dict[str, Any]] = None
    source_refs: Optional[List[Dict[str, Any]]] = None


class ProposalResponse(ProposalBase):
    """Proposal response schema."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
