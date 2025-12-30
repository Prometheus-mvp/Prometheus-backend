"""Entities API endpoints."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import delete, select, update

from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.models import Entity
from app.schemas.entity import EntityCreate, EntityResponse, EntityUpdate

router = APIRouter(prefix="/entities", tags=["entities"])
logger = logging.getLogger(__name__)


@router.get("", response_model=List[EntityResponse])
async def list_entities(
    db: DatabaseSession,
    user_id: UserID,
    kind: Optional[str] = Query(default=None, description="Filter by kind"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> List[EntityResponse]:
    """List entities for the current user."""

    async def _operation():
        stmt = (
            select(Entity)
            .where(Entity.user_id == user_id)
            .order_by(Entity.name)
            .limit(limit)
            .offset(offset)
        )
        if kind:
            stmt = stmt.where(Entity.kind == kind)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Listed entities",
        error_message="Failed to list entities",
        user_id=user_id,
        operation_name="entities_list",
        commit_on_success=False,
    )


@router.post("", response_model=EntityResponse)
async def create_entity(
    payload: EntityCreate,
    db: DatabaseSession,
    user_id: UserID,
) -> EntityResponse:
    """Create a new entity."""

    async def _operation():
        entity = Entity(user_id=user_id, **payload.model_dump())
        db.add(entity)
        await db.flush()
        await db.refresh(entity)
        return entity

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Created entity",
        error_message="Failed to create entity",
        user_id=user_id,
        operation_name="entities_create",
        commit_on_success=True,
    )


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> EntityResponse:
    """Get a specific entity."""

    async def _operation():
        result = await db.execute(
            select(Entity).where(Entity.id == entity_id, Entity.user_id == user_id)
        )
        entity = result.scalar_one_or_none()
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
        return entity

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Fetched entity",
        error_message="Failed to get entity",
        user_id=user_id,
        operation_name="entities_get",
        commit_on_success=False,
    )


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: UUID,
    payload: EntityUpdate,
    db: DatabaseSession,
    user_id: UserID,
) -> EntityResponse:
    """Update an entity."""

    async def _operation():
        stmt = (
            update(Entity)
            .where(Entity.id == entity_id, Entity.user_id == user_id)
            .values(**{k: v for k, v in payload.model_dump().items() if v is not None})
            .returning(Entity)
        )
        result = await db.execute(stmt)
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
        return row[0]

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Updated entity",
        error_message="Failed to update entity",
        user_id=user_id,
        operation_name="entities_update",
        commit_on_success=True,
    )


@router.delete("/{entity_id}", status_code=204)
async def delete_entity(
    entity_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> None:
    """Delete an entity."""

    async def _operation():
        stmt = (
            delete(Entity)
            .where(Entity.id == entity_id, Entity.user_id == user_id)
            .returning(Entity.id)
        )
        result = await db.execute(stmt)
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
        return None

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Deleted entity",
        error_message="Failed to delete entity",
        user_id=user_id,
        operation_name="entities_delete",
        commit_on_success=True,
    )


