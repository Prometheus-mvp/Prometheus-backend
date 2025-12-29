"""Tests for app.core.logging module."""

import logging
import json
from app.core.logging import JSONFormatter, setup_logging


def test_json_formatter_basic():
    """Test JSONFormatter formats log records as JSON."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    output = formatter.format(record)
    parsed = json.loads(output)

    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test_logger"
    assert parsed["message"] == "Test message"
    assert parsed["module"] == "test"
    assert parsed["function"] == "<module>"
    assert parsed["line"] == 42
    assert "timestamp" in parsed


def test_json_formatter_with_exception():
    """Test JSONFormatter includes exception info."""
    formatter = JSONFormatter()

    try:
        raise ValueError("Test error")
    except ValueError:
        import sys

        exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        output = formatter.format(record)
        parsed = json.loads(output)

        assert "exception" in parsed
        assert "ValueError: Test error" in parsed["exception"]


def test_setup_logging():
    """Test setup_logging configures logging."""
    # Save original handlers
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers.copy()

    try:
        setup_logging("DEBUG")

        assert root_logger.level == logging.DEBUG
        assert len(root_logger.handlers) > 0
        assert isinstance(root_logger.handlers[0].formatter, JSONFormatter)
    finally:
        # Restore original handlers
        root_logger.handlers = original_handlers


def test_setup_logging_default_level():
    """Test setup_logging with default log level."""
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers.copy()

    try:
        setup_logging()
        assert root_logger.level == logging.INFO
    finally:
        root_logger.handlers = original_handlers
