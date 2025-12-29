"""User Pydantic schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserBase(BaseModel):
    """Base user schema."""

    email: Optional[str] = None
    display_name: Optional[str] = None
    timezone: str = "UTC"


class UserCreate(UserBase):
    """User creation schema."""

    id: UUID  # Supabase Auth user ID


class UserUpdate(UserBase):
    """User update schema."""

    pass


class UserResponse(UserBase):
    """User response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
