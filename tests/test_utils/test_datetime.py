"""Tests for app.utils.datetime module."""

from datetime import datetime, timezone
import pytz
from app.utils.datetime import utcnow, to_utc, from_utc


def test_utcnow():
    """Test utcnow returns current UTC time."""
    result = utcnow()
    assert result.tzinfo == timezone.utc
    assert isinstance(result, datetime)


def test_to_utc_naive_no_tz():
    """Test to_utc with naive datetime and no timezone."""
    dt = datetime(2025, 1, 15, 10, 30, 0)
    result = to_utc(dt)
    assert result.tzinfo == timezone.utc
    assert result.hour == 10  # Assumes UTC


def test_to_utc_with_timezone():
    """Test to_utc with timezone conversion."""
    dt = datetime(2025, 1, 15, 10, 30, 0)
    result = to_utc(dt, tz="America/New_York")
    assert result.tzinfo == timezone.utc
    # 10:30 EST/EDT should be 15:30 or 14:30 UTC depending on DST
    assert result.hour in [14, 15]


def test_to_utc_aware_datetime():
    """Test to_utc with timezone-aware datetime."""
    tz = pytz.timezone("Europe/London")
    dt = tz.localize(datetime(2025, 1, 15, 10, 30, 0))
    result = to_utc(dt)
    assert result.tzinfo == timezone.utc
    assert result.hour == 10  # London is UTC in winter


def test_from_utc():
    """Test from_utc converts UTC to target timezone."""
    dt = datetime(2025, 1, 15, 15, 30, 0, tzinfo=timezone.utc)
    result = from_utc(dt, tz="America/New_York")
    assert result.hour in [10, 11]  # Depending on DST


def test_from_utc_naive():
    """Test from_utc with naive datetime assumes UTC."""
    dt = datetime(2025, 1, 15, 15, 30, 0)
    result = from_utc(dt, tz="America/Los_Angeles")
    assert result.hour in [7, 8]  # PST/PDT
