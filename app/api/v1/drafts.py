"""Drafts API endpoints."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import delete, select, update

from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.models import Draft
from app.schemas.draft import DraftCreate, DraftResponse, DraftUpdate

router = APIRouter(prefix="/drafts", tags=["drafts"])
logger = logging.getLogger(__name__)


@router.get("", response_model=List[DraftResponse])
async def list_drafts(
    db: DatabaseSession,
    user_id: UserID,
    kind: Optional[str] = Query(default=None, description="Filter by kind"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> List[DraftResponse]:
    """List drafts for the current user."""

    async def _operation():
        stmt = (
            select(Draft)
            .where(Draft.user_id == user_id)
            .order_by(Draft.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if kind:
            stmt = stmt.where(Draft.kind == kind)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Listed drafts",
        error_message="Failed to list drafts",
        user_id=user_id,
        operation_name="drafts_list",
        commit_on_success=False,
    )


@router.post("", response_model=DraftResponse)
async def create_draft(
    payload: DraftCreate,
    db: DatabaseSession,
    user_id: UserID,
) -> DraftResponse:
    """Create a new draft."""

    async def _operation():
        draft = Draft(user_id=user_id, **payload.model_dump())
        db.add(draft)
        await db.flush()
        await db.refresh(draft)
        return draft

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Created draft",
        error_message="Failed to create draft",
        user_id=user_id,
        operation_name="drafts_create",
        commit_on_success=True,
    )


@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft(
    draft_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> DraftResponse:
    """Get a specific draft."""

    async def _operation():
        result = await db.execute(
            select(Draft).where(Draft.id == draft_id, Draft.user_id == user_id)
        )
        draft = result.scalar_one_or_none()
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found"
            )
        return draft

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Fetched draft",
        error_message="Failed to get draft",
        user_id=user_id,
        operation_name="drafts_get",
        commit_on_success=False,
    )


@router.put("/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: UUID,
    payload: DraftUpdate,
    db: DatabaseSession,
    user_id: UserID,
) -> DraftResponse:
    """Update a draft."""

    async def _operation():
        stmt = (
            update(Draft)
            .where(Draft.id == draft_id, Draft.user_id == user_id)
            .values(**{k: v for k, v in payload.model_dump().items() if v is not None})
            .returning(Draft)
        )
        result = await db.execute(stmt)
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found"
            )
        return row[0]

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Updated draft",
        error_message="Failed to update draft",
        user_id=user_id,
        operation_name="drafts_update",
        commit_on_success=True,
    )


@router.delete("/{draft_id}", status_code=204)
async def delete_draft(
    draft_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> None:
    """Delete a draft."""

    async def _operation():
        stmt = (
            delete(Draft)
            .where(Draft.id == draft_id, Draft.user_id == user_id)
            .returning(Draft.id)
        )
        result = await db.execute(stmt)
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found"
            )
        return None

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Deleted draft",
        error_message="Failed to delete draft",
        user_id=user_id,
        operation_name="drafts_delete",
        commit_on_success=True,
    )
