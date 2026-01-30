"""Tests for summarization job."""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4


@pytest.mark.asyncio
async def test_run_summarization():
    """Test run_summarization job."""
    from app.jobs.summarization import run_summarization

    user_id = str(uuid4())
    mock_db = AsyncMock()

    with patch("app.jobs.summarization.summarize_agent") as mock_agent:
        mock_agent.summarize = AsyncMock(
            return_value={"summary": "Test summary", "key_points": ["point1"]}
        )

        result = await run_summarization(mock_db, user_id=user_id, hours=2)

        mock_agent.summarize.assert_called_once_with(
            mock_db, user_id=user_id, prompt="summarize", hours=2, sources=None
        )

    assert result["summary"] == "Test summary"
    assert result["key_points"] == ["point1"]
