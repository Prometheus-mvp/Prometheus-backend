"""Threads API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.models import Thread
from app.schemas.thread import ThreadResponse

router = APIRouter(prefix="/threads", tags=["threads"])


@router.get("", response_model=List[ThreadResponse])
async def list_threads(
    db: DatabaseSession,
    user_id: UserID,
    source: Optional[str] = Query(default=None, description="Filter by source"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> List[ThreadResponse]:
    """List threads for the current user."""
    async def _operation():
        stmt = (
            select(Thread)
            .where(Thread.user_id == user_id)
            .order_by(Thread.last_event_at.desc().nulls_last())
            .limit(limit)
            .offset(offset)
        )
        if source:
            stmt = stmt.where(Thread.source == source)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Listed threads",
        error_message="Failed to list threads",
        user_id=user_id,
        operation_name="threads_list",
        commit_on_success=False,
    )


@router.get("/{thread_id}", response_model=ThreadResponse)
async def get_thread(
    thread_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> ThreadResponse:
    """Get a specific thread."""
    async def _operation():
        result = await db.execute(
            select(Thread).where(Thread.id == thread_id, Thread.user_id == user_id)
        )
        thread = result.scalar_one_or_none()
        if not thread:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")
        return thread

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Fetched thread",
        error_message="Failed to get thread",
        user_id=user_id,
        operation_name="threads_get",
        commit_on_success=False,
    )


