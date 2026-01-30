"""Tests for ingestion job."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4


@pytest.mark.asyncio
async def test_ingest_events_for_user_no_accounts():
    """Test ingestion when user has no linked accounts."""
    from app.jobs.ingestion import ingest_events_for_user

    user_id = str(uuid4())
    mock_db = AsyncMock()
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    await ingest_events_for_user(mock_db, user_id)

    # Should query for linked accounts
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_ingest_events_for_user_with_slack():
    """Test ingestion with Slack account."""
    from app.jobs.ingestion import ingest_events_for_user
    from app.models.linked_account import LinkedAccount

    user_id = uuid4()
    account_id = uuid4()
    mock_account = LinkedAccount(
        id=account_id,
        user_id=user_id,
        provider="slack",
        provider_account_id="U123",
        status="active",
    )

    mock_db = AsyncMock()
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = [mock_account]
    mock_db.execute = AsyncMock(return_value=mock_result)

    mock_slack = Mock()
    mock_slack.provider = "slack"
    mock_slack.fetch_events = AsyncMock(return_value=[])

    with patch("app.jobs.ingestion.slack_connector", mock_slack):
        await ingest_events_for_user(mock_db, str(user_id))

    mock_slack.fetch_events.assert_called_once()
