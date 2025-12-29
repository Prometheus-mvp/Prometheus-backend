"""Tests for connector API endpoints."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4


@pytest.mark.asyncio
async def test_slack_oauth_initiate():
    """Test Slack OAuth initiation."""
    from app.api.v1.connectors import slack_oauth_initiate

    user_id = str(uuid4())
    mock_db = AsyncMock()

    with patch("app.api.v1.connectors.slack_connector") as mock_slack:
        mock_slack.build_auth_url = AsyncMock(
            return_value=("https://slack.com/oauth/authorize?...", "state123")
        )

        response = await slack_oauth_initiate(db=mock_db, user_id=user_id)

        assert response.auth_url.startswith("https://slack.com/oauth/authorize")
        assert response.state == "state123"


@pytest.mark.asyncio
async def test_list_linked_accounts():
    """Test listing linked accounts."""
    from app.api.v1.connectors import list_linked_accounts

    user_id = str(uuid4())
    mock_db = AsyncMock()
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await list_linked_accounts(db=mock_db, user_id=user_id)

    assert response == []


@pytest.mark.asyncio
async def test_delete_linked_account_not_found():
    """Test deleting linked account that doesn't exist."""
    from app.api.v1.connectors import delete_linked_account
    from fastapi import HTTPException

    user_id = str(uuid4())
    account_id = uuid4()
    mock_db = AsyncMock()
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc_info:
        await delete_linked_account(account_id=account_id, db=mock_db, user_id=user_id)

    assert exc_info.value.status_code == 404
