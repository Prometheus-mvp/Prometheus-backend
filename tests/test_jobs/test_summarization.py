"""Tests for summarization job."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone, timedelta
from uuid import uuid4


@pytest.mark.asyncio
async def test_run_summarization():
    """Test run_summarization job."""
    from app.jobs.summarization import run_summarization
    
    user_id = str(uuid4())
    window_start = datetime.now(timezone.utc) - timedelta(hours=2)
    window_end = datetime.now(timezone.utc)
    
    mock_db = AsyncMock()
    
    with patch('app.jobs.summarization.summarize_events') as mock_summarize:
        mock_summarize.return_value = {
            "summary": "Test summary",
            "key_points": ["point1"],
            "source_refs": []
        }
        
        await run_summarization(mock_db, user_id, window_start, window_end)
        
        mock_summarize.assert_called_once()
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

