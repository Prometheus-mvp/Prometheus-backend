"""Calendar CRUD endpoints."""

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import delete, select, update

from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.models import CalendarEvent
from app.schemas.calendar import (
    CalendarEventCreate,
    CalendarEventListResponse,
    CalendarEventResponse,
    CalendarEventUpdate,
)

router = APIRouter(prefix="/calendar/events", tags=["calendar"])
logger = logging.getLogger(__name__)


@router.get("", response_model=CalendarEventListResponse)
async def list_calendar_events(
    db: DatabaseSession,
    user_id: UserID,
    start_date: datetime | None = Query(
        default=None, description="Filter events starting from this date"
    ),
    end_date: datetime | None = Query(
        default=None, description="Filter events ending before this date"
    ),
    limit: int = Query(default=50, ge=1, le=500, description="Maximum number of events to return"),
    offset: int = Query(default=0, ge=0, description="Number of events to skip"),
) -> CalendarEventListResponse:
    """List calendar events for the current user with optional filters."""
    async def _operation():
        stmt = (
            select(CalendarEvent)
            .where(CalendarEvent.user_id == user_id)
            .order_by(CalendarEvent.start_at.asc())
            .limit(limit)
            .offset(offset)
        )

        if start_date:
            stmt = stmt.where(CalendarEvent.start_at >= start_date)
        if end_date:
            stmt = stmt.where(CalendarEvent.end_at <= end_date)

        result = await db.execute(stmt)
        events = list(result.scalars().all())

        count_stmt = select(CalendarEvent).where(CalendarEvent.user_id == user_id)
        if start_date:
            count_stmt = count_stmt.where(CalendarEvent.start_at >= start_date)
        if end_date:
            count_stmt = count_stmt.where(CalendarEvent.end_at <= end_date)
        total_result = await db.execute(count_stmt)
        total = len(list(total_result.scalars().all()))

        return CalendarEventListResponse(events=events, total=total)

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Listed calendar events",
        error_message="Failed to retrieve calendar events",
        user_id=user_id,
        operation_name="calendar_list",
        commit_on_success=False,
    )


@router.get("/{event_id}", response_model=CalendarEventResponse)
async def get_calendar_event(
    event_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> CalendarEventResponse:
    """Get a specific calendar event."""
    async def _operation():
        result = await db.execute(
            select(CalendarEvent).where(
                CalendarEvent.id == event_id, CalendarEvent.user_id == user_id
            )
        )
        event = result.scalar_one_or_none()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Calendar event not found"
            )
        return event

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Fetched calendar event",
        error_message="Failed to retrieve calendar event",
        user_id=user_id,
        operation_name="calendar_get",
        commit_on_success=False,
    )


@router.post("", response_model=CalendarEventResponse)
async def create_calendar_event(
    payload: CalendarEventCreate,
    db: DatabaseSession,
    user_id: UserID,
) -> CalendarEventResponse:
    """Create a new calendar event."""
    async def _operation():
        evt = CalendarEvent(user_id=user_id, **payload.model_dump())
        db.add(evt)
        await db.flush()
        await db.refresh(evt)
        return evt

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Created calendar event",
        error_message="Failed to create calendar event",
        user_id=user_id,
        operation_name="calendar_create",
        commit_on_success=True,
    )


@router.put("/{event_id}", response_model=CalendarEventResponse)
async def update_calendar_event(
    event_id: UUID,
    payload: CalendarEventUpdate,
    db: DatabaseSession,
    user_id: UserID,
) -> CalendarEventResponse:
    """Update a calendar event."""
    async def _operation():
        if payload.start_at is not None or payload.end_at is not None:
            existing = await db.execute(
                select(CalendarEvent).where(
                    CalendarEvent.id == event_id, CalendarEvent.user_id == user_id
                )
            )
            existing_event = existing.scalar_one_or_none()
            if not existing_event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Calendar event not found",
                )

            start_at = payload.start_at if payload.start_at is not None else existing_event.start_at
            end_at = payload.end_at if payload.end_at is not None else existing_event.end_at

            if end_at <= start_at:
                raise ValueError("end_at must be after start_at")

        stmt = (
            update(CalendarEvent)
            .where(CalendarEvent.id == event_id, CalendarEvent.user_id == user_id)
            .values(**{k: v for k, v in payload.model_dump().items() if v is not None})
            .returning(CalendarEvent)
        )
        result = await db.execute(stmt)
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Calendar event not found"
            )
        return row[0]

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Updated calendar event",
        error_message="Failed to update calendar event",
        user_id=user_id,
        operation_name="calendar_update",
        commit_on_success=True,
    )


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar_event(
    event_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> None:
    """Delete a calendar event."""
    async def _operation():
        stmt = (
            delete(CalendarEvent)
            .where(CalendarEvent.id == event_id, CalendarEvent.user_id == user_id)
            .returning(CalendarEvent.id)
        )
        result = await db.execute(stmt)
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Calendar event not found"
            )
        return None

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Deleted calendar event",
        error_message="Failed to delete calendar event",
        user_id=user_id,
        operation_name="calendar_delete",
        commit_on_success=True,
    )
