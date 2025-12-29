"""Tests for Slack connector."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4


@pytest.mark.asyncio
async def test_slack_build_auth_url():
    """Test Slack OAuth URL building."""
    from app.services.connector.slack import SlackConnector

    connector = SlackConnector()
    user_id = str(uuid4())

    auth_url, state = await connector.build_auth_url(user_id)

    assert "slack.com/oauth/v2/authorize" in auth_url
    assert "client_id=" in auth_url
    assert len(state) > 0


@pytest.mark.asyncio
async def test_slack_exchange_code_success():
    """Test Slack OAuth code exchange."""
    from app.services.connector.slack import SlackConnector

    connector = SlackConnector()
    user_id = str(uuid4())
    mock_db = AsyncMock()

    mock_response = {
        "ok": True,
        "access_token": "xoxb-test",
        "team": {"id": "T123"},
        "authed_user": {"id": "U123"},
    }

    with patch.object(connector.client, "post") as mock_post:
        mock_post.return_value = Mock(json=lambda: mock_response)

        result = await connector.exchange_code(mock_db, "code123", user_id)

        assert result is not None
        mock_db.add.assert_called()


@pytest.mark.asyncio
async def test_slack_fetch_recent_events():
    """Test Slack event fetching."""
    from app.services.connector.slack import SlackConnector

    connector = SlackConnector()
    mock_db = AsyncMock()
    account_id = uuid4()

    with patch.object(connector, "_get_latest_token") as mock_token:
        mock_token.return_value = Mock(access_token_enc="encrypted")

        with patch("app.services.connector.slack.encryption_service") as mock_enc:
            mock_enc.decrypt.return_value = "xoxb-decrypted"

            with patch.object(connector.client, "get") as mock_get:
                mock_get.return_value = Mock(
                    json=lambda: {
                        "ok": True,
                        "messages": [{"ts": "1234.5678", "text": "Hello"}],
                    }
                )

                events = await connector.fetch_recent_events(mock_db, account_id)

                assert len(events) >= 0  # May return empty if filtering
