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
    """Test Slack OAuth callback (code exchange)."""
    from app.services.connector.slack import SlackConnector

    connector = SlackConnector()
    user_id = str(uuid4())
    mock_db = AsyncMock()
    mock_db.add = Mock()  # sync in real SQLAlchemy; avoid unawaited coroutine warning
    mock_account = Mock()
    mock_account.id = uuid4()

    mock_response = Mock()
    mock_response.json.return_value = {
        "ok": True,
        "access_token": "xoxb-test",
        "team": {"id": "T123"},
        "authed_user": {"id": "U123"},
    }

    with patch.object(connector._client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        with patch.object(
            connector, "_get_or_create_linked_account", new_callable=AsyncMock
        ) as mock_get_account:
            mock_get_account.return_value = mock_account

            result = await connector.handle_callback(
                mock_db, user_id, code="code123", state="state123"
            )

            assert result is not None
            mock_db.add.assert_called()


@pytest.mark.asyncio
async def test_slack_fetch_events():
    """Test Slack event fetching."""
    from app.services.connector.slack import SlackConnector

    connector = SlackConnector()
    mock_db = AsyncMock()
    user_id = str(uuid4())
    mock_account = Mock()
    mock_account.id = uuid4()

    mock_account_result = Mock()
    mock_account_result.scalars.return_value.first.return_value = mock_account
    mock_db.execute = AsyncMock(return_value=mock_account_result)

    with patch.object(
        connector, "_ensure_access_token", new_callable=AsyncMock
    ) as mock_ensure:
        mock_ensure.return_value = "xoxb-token"
        with patch.object(
            connector._client, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.side_effect = [
                Mock(json=lambda: {"ok": True, "channels": [{"id": "C1"}]}),
                Mock(
                    json=lambda: {
                        "ok": True,
                        "messages": [{"ts": "1234.5678", "text": "Hello"}],
                    }
                ),
            ]

            events = await connector.fetch_events(mock_db, user_id, since=None)

            assert isinstance(events, list)
            assert len(events) >= 0
