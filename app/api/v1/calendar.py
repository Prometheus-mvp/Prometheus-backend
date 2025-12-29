"""Calendar CRUD endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import delete, select, update

from app.api.deps import DatabaseSession, UserID
from app.models import CalendarEvent
from app.schemas.calendar import (
    CalendarEventCreate,
    CalendarEventListResponse,
    CalendarEventResponse,
    CalendarEventUpdate,
)

router = APIRouter(prefix="/calendar/events", tags=["calendar"])


@router.get("", response_model=CalendarEventListResponse)
async def list_calendar_events(
    db: DatabaseSession,
    user_id: UserID,
) -> CalendarEventListResponse:
    result = await db.execute(
        select(CalendarEvent).where(CalendarEvent.user_id == user_id)
    )
    events = list(result.scalars().all())
    return CalendarEventListResponse(events=events, total=len(events))


@router.post("", response_model=CalendarEventResponse)
async def create_calendar_event(
    payload: CalendarEventCreate,
    db: DatabaseSession,
    user_id: UserID,
) -> CalendarEventResponse:
    evt = CalendarEvent(user_id=user_id, **payload.model_dump())
    db.add(evt)
    await db.flush()
    return evt


@router.put("/{event_id}", response_model=CalendarEventResponse)
async def update_calendar_event(
    event_id: UUID,
    payload: CalendarEventUpdate,
    db: DatabaseSession,
    user_id: UserID,
) -> CalendarEventResponse:
    stmt = (
        update(CalendarEvent)
        .where(CalendarEvent.id == event_id, CalendarEvent.user_id == user_id)
        .values(**{k: v for k, v in payload.model_dump().items() if v is not None})
        .returning(CalendarEvent)
    )
    result = await db.execute(stmt)
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    return row[0]


@router.delete("/{event_id}", status_code=204)
async def delete_calendar_event(
    event_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> None:
    stmt = delete(CalendarEvent).where(
        CalendarEvent.id == event_id, CalendarEvent.user_id == user_id
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    return None
