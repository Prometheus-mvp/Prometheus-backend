"""Tests for base connector."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4


@pytest.mark.asyncio
async def test_base_connector_store_tokens():
    """Test base connector token storage."""
    from app.services.connector.base import BaseConnector, TokenData

    # Create concrete implementation for testing
    class TestConnector(BaseConnector):
        async def build_auth_url(self, user_id: str):
            return ("https://example.com", "state")

        async def exchange_code(self, db, code: str, user_id: str):
            return {"provider_account_id": "test123"}

        async def fetch_recent_events(self, db, linked_account_id):
            return []

    connector = TestConnector()
    mock_db = AsyncMock()
    user_id = uuid4()
    account_id = uuid4()

    token_data = TokenData(
        access_token="test_access",
        refresh_token="test_refresh",
        expires_in=3600,
        scopes="read write",
    )

    with patch("app.services.connector.base.encryption_service") as mock_enc:
        mock_enc.encrypt.side_effect = lambda x: f"encrypted_{x}"

        await connector._store_tokens(
            mock_db, user_id, account_id, token_data, token_type="bearer"
        )

        mock_db.add.assert_called_once()


@pytest.mark.asyncio
async def test_base_connector_get_latest_token():
    """Test getting latest token."""
    from app.services.connector.base import BaseConnector
    from app.models.oauth_token import OAuthToken

    class TestConnector(BaseConnector):
        async def build_auth_url(self, user_id: str):
            return ("https://example.com", "state")

        async def exchange_code(self, db, code: str, user_id: str):
            return {"provider_account_id": "test123"}

        async def fetch_recent_events(self, db, linked_account_id):
            return []

    connector = TestConnector()
    mock_db = AsyncMock()
    account_id = uuid4()

    mock_token = OAuthToken(
        id=uuid4(),
        user_id=uuid4(),
        linked_account_id=account_id,
        token_type="bearer",
        access_token_enc="encrypted_access",
        refresh_token_enc="encrypted_refresh",
    )

    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_token
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await connector._get_latest_token(mock_db, account_id)

    assert result == mock_token
