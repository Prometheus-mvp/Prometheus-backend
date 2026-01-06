"""Entity Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class EntityBase(BaseModel):
    """Base entity schema."""

    kind: str  # person | org | project | topic
    name: str
    aliases: List[str] = []
    metadata: Dict[str, Any] = {}


class EntityCreate(EntityBase):
    """Entity creation schema."""

    pass


class EntityUpdate(BaseModel):
    """Entity update schema."""

    kind: Optional[str] = None
    name: Optional[str] = None
    aliases: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class EntityResponse(EntityBase):
    """Entity response schema."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

