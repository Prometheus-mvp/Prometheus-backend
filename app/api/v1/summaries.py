"""Summaries API endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.models import Summary
from app.schemas.summary import SummaryResponse

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.get("", response_model=List[SummaryResponse])
async def list_summaries(
    db: DatabaseSession,
    user_id: UserID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> List[SummaryResponse]:
    """List summaries for the current user."""

    async def _operation():
        stmt = (
            select(Summary)
            .where(Summary.user_id == user_id)
            .order_by(Summary.window_start.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Listed summaries",
        error_message="Failed to list summaries",
        user_id=user_id,
        operation_name="summaries_list",
        commit_on_success=False,
    )


@router.get("/{summary_id}", response_model=SummaryResponse)
async def get_summary(
    summary_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> SummaryResponse:
    """Get a specific summary."""

    async def _operation():
        result = await db.execute(
            select(Summary).where(Summary.id == summary_id, Summary.user_id == user_id)
        )
        summary = result.scalar_one_or_none()
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found"
            )
        return summary

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Fetched summary",
        error_message="Failed to get summary",
        user_id=user_id,
        operation_name="summaries_get",
        commit_on_success=False,
    )
