"""Tests for LinkedAccount model."""

from uuid import uuid4
from app.models.linked_account import LinkedAccount


def test_linked_account_creation():
    """Test LinkedAccount model can be instantiated."""
    user_id = uuid4()
    account = LinkedAccount(
        user_id=user_id,
        provider="slack",
        provider_account_id="U12345",
        scopes="channels:read,chat:write",
        status="active",
    )

    assert account.user_id == user_id
    assert account.provider == "slack"
    assert account.provider_account_id == "U12345"
    assert account.scopes == "channels:read,chat:write"
    assert account.status == "active"


def test_linked_account_defaults():
    """Test LinkedAccount default values."""
    account = LinkedAccount(
        user_id=uuid4(), provider="telegram", provider_account_id="123456"
    )
    # metadata has server default JSONB {}
    assert account.scopes is None
