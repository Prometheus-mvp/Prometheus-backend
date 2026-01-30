"""Tasks API endpoints."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import delete, select, update

from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.models import Task
from app.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    db: DatabaseSession,
    user_id: UserID,
    status: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
) -> TaskListResponse:
    """List tasks with optional filters."""

    async def _operation():
        stmt = select(Task).where(Task.user_id == user_id)
        if status:
            stmt = stmt.where(Task.status == status)
        if priority:
            stmt = stmt.where(Task.priority == priority)
        result = await db.execute(stmt)
        tasks = list(result.scalars().all())

        by_priority = {"high": 0, "medium": 0, "low": 0}
        for t in tasks:
            if t.priority in by_priority:
                by_priority[t.priority] += 1
        return TaskListResponse(tasks=tasks, total=len(tasks), by_priority=by_priority)

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Listed tasks",
        error_message="Failed to list tasks",
        user_id=user_id,
        operation_name="tasks_list",
        commit_on_success=False,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> TaskResponse:
    """Get a specific task."""

    async def _operation():
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        return task

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Retrieved task",
        error_message="Failed to retrieve task",
        user_id=user_id,
        operation_name="tasks_get",
        commit_on_success=False,
    )


@router.post("", response_model=TaskResponse)
async def create_task(
    payload: TaskCreate,
    db: DatabaseSession,
    user_id: UserID,
) -> TaskResponse:
    """Create a new task."""

    async def _operation():
        task = Task(user_id=user_id, **payload.model_dump())
        db.add(task)
        await db.flush()
        await db.refresh(task)
        return task

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Created task",
        error_message="Failed to create task",
        user_id=user_id,
        operation_name="tasks_create",
        commit_on_success=True,
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    db: DatabaseSession,
    user_id: UserID,
) -> TaskResponse:
    """Update a task."""

    async def _operation():
        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.user_id == user_id)
            .values(**{k: v for k, v in payload.model_dump().items() if v is not None})
            .returning(Task)
        )
        result = await db.execute(stmt)
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        return row[0]

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Updated task",
        error_message="Failed to update task",
        user_id=user_id,
        operation_name="tasks_update",
        commit_on_success=True,
    )


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> None:
    """Delete a task."""

    async def _operation():
        stmt = (
            delete(Task)
            .where(Task.id == task_id, Task.user_id == user_id)
            .returning(Task.id)
        )
        result = await db.execute(stmt)
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        return None

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Deleted task",
        error_message="Failed to delete task",
        user_id=user_id,
        operation_name="tasks_delete",
        commit_on_success=True,
    )
