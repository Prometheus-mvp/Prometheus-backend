"""Tests for connector schemas."""

from app.schemas.connector import (
    LinkedAccountCreate,
    OAuthInitiateResponse,
    TelegramAuthInitiateRequest,
)


def test_linked_account_create():
    """Test LinkedAccountCreate schema."""
    account = LinkedAccountCreate(
        provider="slack",
        provider_account_id="U123",
        scopes="channels:read",
        status="active",
    )

    assert account.provider == "slack"
    assert account.provider_account_id == "U123"


def test_oauth_initiate_response():
    """Test OAuthInitiateResponse schema."""
    response = OAuthInitiateResponse(
        auth_url="https://slack.com/oauth/authorize", state="state123"
    )

    assert response.auth_url.startswith("https://")
    assert len(response.state) > 0


def test_telegram_auth_initiate_request():
    """Test TelegramAuthInitiateRequest schema."""
    request = TelegramAuthInitiateRequest(phone_number="+1234567890")

    assert request.phone_number == "+1234567890"
