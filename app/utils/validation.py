"""Validation utilities for prompts and requests."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from app.agents.source_extractor import VALID_SOURCES


def validate_sources(sources: Optional[List[str]]) -> Tuple[bool, List[str], str]:
    """
    Validate source list.

    Returns:
        (is_valid, valid_sources, error_message)
    """
    if not sources:
        return False, [], "No sources specified"

    valid = []
    invalid = []
    for source in sources:
        source_lower = source.lower()
        if source_lower in VALID_SOURCES:
            valid.append(source_lower)
        else:
            invalid.append(source)

    if invalid:
        return (
            False,
            valid,
            f"Invalid sources: {', '.join(invalid)}. Valid sources: {', '.join(VALID_SOURCES)}",
        )

    return True, valid, ""


def validate_time_range(
    start_time: Optional[datetime],
    end_time: Optional[datetime],
) -> Tuple[bool, str]:
    """
    Validate time range.

    Returns:
        (is_valid, error_message)
    """
    if not start_time and not end_time:
        return False, "No time range specified"

    if not start_time:
        return False, "Start time not specified"

    if not end_time:
        return False, "End time not specified"

    if end_time <= start_time:
        return False, "End time must be after start time"

    # Check if times are too far in the future
    now = datetime.now(timezone.utc)
    if start_time > now:
        return False, "Start time cannot be in the future"

    return True, ""


def needs_clarification(
    sources: Optional[List[str]],
    start_time: Optional[datetime],
    end_time: Optional[datetime],
) -> Tuple[bool, List[str], str]:
    """
    Check if prompt needs clarification from user.

    Returns:
        (needs_clarification, missing_fields, clarification_message)
    """
    missing = []
    messages = []

    # Check sources
    if not sources:
        missing.append("sources")
        messages.append(
            "Which application(s) should I check? (slack, telegram, outlook)"
        )

    # Check time range
    if not start_time or not end_time:
        missing.append("time_range")
        messages.append(
            "What time period should I look at? (e.g., 'last 2 hours', 'today', 'yesterday')"
        )

    if missing:
        return True, missing, " ".join(messages)

    return False, [], ""


__all__ = [
    "validate_sources",
    "validate_time_range",
    "needs_clarification",
    "VALID_SOURCES",
]
