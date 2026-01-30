"""Tests for source and time extractors."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest


class TestSourceExtractor:
    """Test SourceExtractor functionality."""

    @pytest.mark.asyncio
    async def test_extract_explicit_slack(self):
        """Test extraction of explicit Slack mention."""
        from app.agents.source_extractor import SourceExtractor

        extractor = SourceExtractor()
        result = await extractor.extract_sources("summarize my slack messages")

        assert "slack" in result["sources"]
        assert result["confidence"] >= 0.9
        assert result["explicit"] is True

    @pytest.mark.asyncio
    async def test_extract_explicit_telegram(self):
        """Test extraction of explicit Telegram mention."""
        from app.agents.source_extractor import SourceExtractor

        extractor = SourceExtractor()
        result = await extractor.extract_sources("what did I get on telegram?")

        assert "telegram" in result["sources"]
        assert result["explicit"] is True

    @pytest.mark.asyncio
    async def test_extract_explicit_outlook(self):
        """Test extraction of explicit Outlook/email mention."""
        from app.agents.source_extractor import SourceExtractor

        extractor = SourceExtractor()
        result = await extractor.extract_sources("check my emails from outlook")

        assert "outlook" in result["sources"]
        assert result["explicit"] is True

    @pytest.mark.asyncio
    async def test_extract_multiple_sources(self):
        """Test extraction of multiple sources."""
        from app.agents.source_extractor import SourceExtractor

        extractor = SourceExtractor()
        result = await extractor.extract_sources(
            "summarize my slack and telegram messages"
        )

        assert "slack" in result["sources"]
        assert "telegram" in result["sources"]

    @pytest.mark.asyncio
    async def test_no_sources_returns_empty(self):
        """Test that prompts without sources return empty list."""
        from app.agents.source_extractor import SourceExtractor

        extractor = SourceExtractor()

        with patch.object(extractor, "complete_json", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "sources": [],
                "confidence": 0.3,
                "explicit": False,
            }

            result = await extractor.extract_sources("summarize my day")

            assert result["sources"] == []
            assert result["explicit"] is False


class TestTimeRangeExtractor:
    """Test TimeRangeExtractor functionality."""

    @pytest.mark.asyncio
    async def test_extract_last_n_hours(self):
        """Test extraction of 'last N hours' pattern."""
        from app.agents.time_extractor import TimeRangeExtractor

        extractor = TimeRangeExtractor()
        result = await extractor.extract_time_range("summarize last 2 hours")

        now = datetime.now(timezone.utc)
        assert result["start_time"] is not None
        assert result["end_time"] is not None
        assert result["confidence"] >= 0.9

        # Check time range is approximately 2 hours
        time_diff = result["end_time"] - result["start_time"]
        assert 1.9 <= time_diff.total_seconds() / 3600 <= 2.1

    @pytest.mark.asyncio
    async def test_extract_last_n_days(self):
        """Test extraction of 'last N days' pattern."""
        from app.agents.time_extractor import TimeRangeExtractor

        extractor = TimeRangeExtractor()
        result = await extractor.extract_time_range("what happened in the last 3 days")

        assert result["start_time"] is not None
        assert result["end_time"] is not None

        time_diff = result["end_time"] - result["start_time"]
        assert 2.9 <= time_diff.total_seconds() / 86400 <= 3.1

    @pytest.mark.asyncio
    async def test_extract_today(self):
        """Test extraction of 'today' pattern."""
        from app.agents.time_extractor import TimeRangeExtractor

        extractor = TimeRangeExtractor()
        result = await extractor.extract_time_range("summarize today")

        assert result["start_time"] is not None
        assert result["end_time"] is not None
        assert result["start_time"].hour == 0
        assert result["start_time"].minute == 0

    @pytest.mark.asyncio
    async def test_extract_yesterday(self):
        """Test extraction of 'yesterday' pattern."""
        from app.agents.time_extractor import TimeRangeExtractor

        extractor = TimeRangeExtractor()
        result = await extractor.extract_time_range("what happened yesterday")

        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)

        assert result["start_time"] is not None
        assert result["start_time"].date() == yesterday.date()

    @pytest.mark.asyncio
    async def test_extract_this_week(self):
        """Test extraction of 'this week' pattern."""
        from app.agents.time_extractor import TimeRangeExtractor

        extractor = TimeRangeExtractor()
        result = await extractor.extract_time_range("summarize this week")

        assert result["start_time"] is not None
        assert result["end_time"] is not None
        # Start should be a Monday
        assert result["start_time"].weekday() == 0

    @pytest.mark.asyncio
    async def test_no_time_returns_none(self):
        """Test that prompts without time return None."""
        from app.agents.time_extractor import TimeRangeExtractor

        extractor = TimeRangeExtractor()

        with patch.object(extractor, "complete_json", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "start_time": None,
                "end_time": None,
                "confidence": 0.3,
                "explicit": False,
            }

            result = await extractor.extract_time_range("summarize my messages")

            assert result["start_time"] is None
            assert result["end_time"] is None
