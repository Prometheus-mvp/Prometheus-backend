"""Connector Pydantic schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class Provider(str, Enum):
    """Supported OAuth providers."""

    SLACK = "slack"
    TELEGRAM = "telegram"
    OUTLOOK = "outlook"


class AccountStatus(str, Enum):
    """Linked account status."""

    ACTIVE = "active"
    REVOKED = "revoked"
    ERROR = "error"


class LinkedAccountBase(BaseModel):
    """Base linked account schema."""

    provider: Provider = Field(
        ..., description="OAuth provider: slack, telegram, or outlook"
    )
    provider_account_id: str = Field(
        ..., description="External provider's account identifier"
    )
    scopes: Optional[str] = Field(None, description="OAuth scopes granted")
    status: AccountStatus = Field(
        default=AccountStatus.ACTIVE, description="Account connection status"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional provider-specific metadata"
    )


class LinkedAccountResponse(LinkedAccountBase):
    """Linked account response schema."""

    id: UUID = Field(..., description="Unique linked account identifier")
    user_id: UUID = Field(..., description="User who owns this linked account")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Account last update timestamp")

    class Config:
        from_attributes = True


class OAuthInitiateResponse(BaseModel):
    """OAuth initiation response."""

    auth_url: str = Field(
        ..., description="URL to redirect user for OAuth authorization"
    )
    state: str = Field(..., description="CSRF protection state token")


class OAuthCallbackResponse(BaseModel):
    """OAuth callback response."""

    linked_account_id: UUID = Field(
        ..., description="Created linked account identifier"
    )
    provider: Provider = Field(..., description="OAuth provider name")
    provider_account_id: str = Field(
        ..., description="External provider's account identifier"
    )
    status: AccountStatus = Field(..., description="Account connection status")


class TelegramAuthInitiateRequest(BaseModel):
    """Telegram auth initiation request."""

    phone_number: str = Field(
        ..., description="Phone number in international format (e.g., +1234567890)"
    )

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format."""
        if not v.startswith("+"):
            raise ValueError("Phone number must start with +")
        if len(v) < 10:
            raise ValueError("Phone number too short")
        return v


class TelegramAuthInitiateResponse(BaseModel):
    """Telegram auth initiation response."""

    auth_session_id: UUID = Field(
        ..., description="Telegram authentication session identifier"
    )
    phone_code_hash: str = Field(..., description="Hash for phone code verification")


class TelegramAuthVerifyRequest(BaseModel):
    """Telegram auth verification request."""

    auth_session_id: UUID = Field(
        ..., description="Telegram authentication session identifier"
    )
    phone_code: str = Field(..., description="SMS verification code")
    phone_code_hash: str = Field(..., description="Hash for phone code verification")
    phone_number: Optional[str] = Field(
        None, description="Phone number (optional, for verification)"
    )


class TelegramAuthVerifyResponse(BaseModel):
    """Telegram auth verification response."""

    linked_account_id: UUID = Field(
        ..., description="Created linked account identifier"
    )
    provider: Literal["telegram"] = Field(..., description="Provider name")
    provider_account_id: str = Field(..., description="Telegram user identifier")
    status: AccountStatus = Field(..., description="Account connection status")
