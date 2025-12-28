"""Connector Pydantic schemas."""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class LinkedAccountBase(BaseModel):
    """Base linked account schema."""
    provider: str = Field(..., description="Provider: slack, telegram, or outlook")
    provider_account_id: str
    scopes: Optional[str] = None
    status: str = "active"
    metadata: Dict[str, Any] = {}


class LinkedAccountCreate(LinkedAccountBase):
    """Linked account creation schema."""
    pass


class LinkedAccountResponse(LinkedAccountBase):
    """Linked account response schema."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OAuthInitiateResponse(BaseModel):
    """OAuth initiation response."""
    auth_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request."""
    code: str
    state: str


class OAuthCallbackResponse(BaseModel):
    """OAuth callback response."""
    linked_account_id: UUID
    provider: str
    provider_account_id: str
    status: str


class TelegramAuthInitiateRequest(BaseModel):
    """Telegram auth initiation request."""
    phone_number: str


class TelegramAuthInitiateResponse(BaseModel):
    """Telegram auth initiation response."""
    auth_session_id: UUID
    phone_code_hash: str


class TelegramAuthVerifyRequest(BaseModel):
    """Telegram auth verification request."""
    auth_session_id: UUID
    phone_code: str
    phone_code_hash: str
    phone_number: Optional[str] = None


class TelegramAuthVerifyResponse(BaseModel):
    """Telegram auth verification response."""
    linked_account_id: UUID
    provider: str
    provider_account_id: str
    status: str

