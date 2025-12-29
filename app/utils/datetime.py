"""Timezone utilities."""

from datetime import datetime, timezone
from typing import Optional

import pytz


def utcnow() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def to_utc(dt: datetime, tz: Optional[str] = None) -> datetime:
    """
    Convert datetime to UTC.

    Args:
        dt: Datetime to convert
        tz: Timezone string (e.g., 'America/New_York'). If None, assumes dt is already in UTC.

    Returns:
        Datetime in UTC
    """
    if tz:
        tz_obj = pytz.timezone(tz)
        if dt.tzinfo is None:
            # Naive datetime - assume it's in the given timezone
            dt = tz_obj.localize(dt)
        else:
            # Aware datetime - convert to given timezone first
            dt = dt.astimezone(tz_obj)

    # Convert to UTC
    if dt.tzinfo is None:
        # Naive datetime - assume UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def from_utc(dt: datetime, tz: str) -> datetime:
    """
    Convert UTC datetime to specified timezone.

    Args:
        dt: UTC datetime
        tz: Target timezone string (e.g., 'America/New_York')

    Returns:
        Datetime in target timezone
    """
    if dt.tzinfo is None:
        # Assume UTC if naive
        dt = dt.replace(tzinfo=timezone.utc)

    tz_obj = pytz.timezone(tz)
    return dt.astimezone(tz_obj)
