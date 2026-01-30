"""Events API endpoints."""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, update

from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.models import Event
from app.schemas.event import EventResponse

router = APIRouter(prefix="/events", tags=["events"])
logger = logging.getLogger(__name__)


@router.get("", response_model=List[EventResponse])
async def list_events(
    db: DatabaseSession,
    user_id: UserID,
    source: Optional[str] = Query(default=None, description="Filter by source"),
    event_type: Optional[str] = Query(default=None, description="Filter by event type"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> List[EventResponse]:
    """List events with optional filters."""

    async def _operation():
        stmt = (
            select(Event)
            .where(Event.user_id == user_id, Event.deleted_at.is_(None))
            .order_by(Event.occurred_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if source:
            stmt = stmt.where(Event.source == source)
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Listed events",
        error_message="Failed to list events",
        user_id=user_id,
        operation_name="events_list",
        commit_on_success=False,
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> EventResponse:
    """Get a specific event."""

    async def _operation():
        result = await db.execute(
            select(Event).where(Event.id == event_id, Event.user_id == user_id)
        )
        event = result.scalar_one_or_none()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )
        return event

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Fetched event",
        error_message="Failed to get event",
        user_id=user_id,
        operation_name="events_get",
        commit_on_success=False,
    )


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> None:
    """Soft delete an event."""

    async def _operation():
        stmt = (
            update(Event)
            .where(Event.id == event_id, Event.user_id == user_id)
            .values(deleted_at=datetime.now(timezone.utc))
        )
        result = await db.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )
        return None

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Deleted event",
        error_message="Failed to delete event",
        user_id=user_id,
        operation_name="events_delete",
        commit_on_success=True,
    )
