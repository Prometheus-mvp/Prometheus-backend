"""Proposals API endpoints."""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.models import Proposal
from app.schemas.proposal import ProposalResponse

router = APIRouter(prefix="/proposals", tags=["proposals"])
logger = logging.getLogger(__name__)


@router.get("", response_model=List[ProposalResponse])
async def list_proposals(
    db: DatabaseSession,
    user_id: UserID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> List[ProposalResponse]:
    """List proposals for the current user."""

    async def _operation():
        stmt = (
            select(Proposal)
            .where(Proposal.user_id == user_id)
            .order_by(Proposal.window_start.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Listed proposals",
        error_message="Failed to list proposals",
        user_id=user_id,
        operation_name="proposals_list",
        commit_on_success=False,
    )


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> ProposalResponse:
    """Get a specific proposal."""

    async def _operation():
        result = await db.execute(
            select(Proposal).where(
                Proposal.id == proposal_id, Proposal.user_id == user_id
            )
        )
        proposal = result.scalar_one_or_none()
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found"
            )
        return proposal

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Fetched proposal",
        error_message="Failed to get proposal",
        user_id=user_id,
        operation_name="proposals_get",
        commit_on_success=False,
    )
