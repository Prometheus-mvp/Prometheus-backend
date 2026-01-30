"""Tests for connector schemas."""

from app.schemas.connector import (
    LinkedAccountBase,
    OAuthInitiateResponse,
    TelegramAuthInitiateRequest,
)


def test_linked_account_base():
    """Test LinkedAccountBase schema (used for creation payloads)."""
    account = LinkedAccountBase(
        provider="slack",
        provider_account_id="U123",
        scopes="channels:read",
        status="active",
    )

    assert account.provider.value == "slack"
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
