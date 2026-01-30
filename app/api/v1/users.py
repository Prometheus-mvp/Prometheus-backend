"""User profile management endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, update

from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.models import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    db: DatabaseSession,
    user_id: UserID,
) -> UserResponse:
    """Get current user profile."""

    async def _operation():
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Fetched current user profile",
        error_message="Failed to get user",
        user_id=user_id,
        operation_name="users_get_me",
        commit_on_success=False,
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    payload: UserUpdate,
    db: DatabaseSession,
    user_id: UserID,
) -> UserResponse:
    """Update current user profile."""

    async def _operation():
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**{k: v for k, v in payload.model_dump().items() if v is not None})
            .returning(User)
        )
        result = await db.execute(stmt)
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return row[0]

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Updated current user profile",
        error_message="Failed to update user",
        user_id=user_id,
        operation_name="users_update_me",
        commit_on_success=True,
    )
