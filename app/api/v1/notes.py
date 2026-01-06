"""Notes API endpoints."""

import logging
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import delete, select, update

from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.models import Note
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])
logger = logging.getLogger(__name__)


@router.get("", response_model=List[NoteResponse])
async def list_notes(
    db: DatabaseSession,
    user_id: UserID,
) -> List[NoteResponse]:
    """List notes for the current user."""
    async def _operation():
        result = await db.execute(
            select(Note)
            .where(Note.user_id == user_id, Note.deleted_at.is_(None))
            .order_by(Note.updated_at.desc())
        )
        return list(result.scalars().all())

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Listed notes",
        error_message="Failed to list notes",
        user_id=user_id,
        operation_name="notes_list",
        commit_on_success=False,
    )


@router.post("", response_model=NoteResponse)
async def create_note(
    payload: NoteCreate,
    db: DatabaseSession,
    user_id: UserID,
) -> NoteResponse:
    """Create a new note."""
    async def _operation():
        note = Note(user_id=user_id, **payload.model_dump())
        db.add(note)
        await db.flush()
        await db.refresh(note)
        return note

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Created note",
        error_message="Failed to create note",
        user_id=user_id,
        operation_name="notes_create",
        commit_on_success=True,
    )


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> NoteResponse:
    """Get a specific note."""
    async def _operation():
        result = await db.execute(
            select(Note).where(Note.id == note_id, Note.user_id == user_id)
        )
        note = result.scalar_one_or_none()
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return note

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Fetched note",
        error_message="Failed to get note",
        user_id=user_id,
        operation_name="notes_get",
        commit_on_success=False,
    )


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    payload: NoteUpdate,
    db: DatabaseSession,
    user_id: UserID,
) -> NoteResponse:
    """Update a note."""
    async def _operation():
        stmt = (
            update(Note)
            .where(Note.id == note_id, Note.user_id == user_id)
            .values(**{k: v for k, v in payload.model_dump().items() if v is not None})
            .returning(Note)
        )
        result = await db.execute(stmt)
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return row[0]

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Updated note",
        error_message="Failed to update note",
        user_id=user_id,
        operation_name="notes_update",
        commit_on_success=True,
    )


@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> None:
    """Soft delete a note."""
    async def _operation():
        stmt = (
            update(Note)
            .where(Note.id == note_id, Note.user_id == user_id)
            .values(deleted_at=datetime.now(timezone.utc))
            .returning(Note.id)
        )
        result = await db.execute(stmt)
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return None

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Deleted note",
        error_message="Failed to delete note",
        user_id=user_id,
        operation_name="notes_delete",
        commit_on_success=True,
    )


