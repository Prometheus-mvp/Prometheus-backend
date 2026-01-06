"""Shared helper utilities for API endpoints."""

import logging
from typing import Any, Callable, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Patterns that should not appear in logs
SENSITIVE_PATTERNS = [
    "code=",
    "token",
    "secret",
    "password",
    "phone",
    "authorization",
    "oauth",
]


def sanitize_error_message(error: Exception) -> str:
    """
    Return a safe error description without leaking secrets.
    """
    error_type = error.__class__.__name__
    error_msg = str(error)

    error_lower = error_msg.lower()
    if any(pattern in error_lower for pattern in SENSITIVE_PATTERNS):
        return f"{error_type} (message hidden)"

    return f"{error_type}: {error_msg[:200]}"


async def handle_operation(
    db: AsyncSession | None,
    operation: Callable[[], Any],
    success_message: str,
    error_message: str,
    user_id: str | None,
    operation_name: str,
    commit_on_success: bool = False,
    additional_context: dict | None = None,
) -> Any:
    """
    Centralized error handling for API operations.
    - Executes the operation
    - Optionally commits on success
    - Rolls back on failure
    - Logs sanitized errors
    """
    try:
        result = await operation()

        if commit_on_success and db:
            await db.commit()

        log_extra = {"operation": operation_name}
        if user_id is not None:
            log_extra["user_id"] = user_id

        if additional_context:
            if hasattr(result, "id"):
                additional_context.setdefault("record_id", str(result.id))
            log_extra.update(additional_context)

        logger.info(success_message, extra=log_extra)
        return result

    except ValueError as exc:
        if db:
            await db.rollback()
        logger.warning(
            f"{operation_name} validation failed",
            extra={
                "operation": operation_name,
                "user_id": user_id,
                "error_type": exc.__class__.__name__,
                "error_sanitized": sanitize_error_message(exc),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        ) from exc

    except HTTPException:
        if db:
            await db.rollback()
        raise

    except Exception as exc:
        if db:
            await db.rollback()
        logger.error(
            f"{operation_name} failed",
            extra={
                "operation": operation_name,
                "user_id": user_id,
                "error_type": exc.__class__.__name__,
                "error_sanitized": sanitize_error_message(exc),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message,
        ) from exc

