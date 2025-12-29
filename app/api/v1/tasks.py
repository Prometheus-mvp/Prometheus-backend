"""Tasks API endpoints."""

from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import DatabaseSession, UserID
from app.models import Task
from app.schemas.task import TaskListResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    db: DatabaseSession,
    user_id: UserID,
    status: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
) -> TaskListResponse:
    """List tasks with optional filters."""
    stmt = select(Task).where(Task.user_id == user_id)
    if status:
        stmt = stmt.where(Task.status == status)
    if priority:
        stmt = stmt.where(Task.priority == priority)
    result = await db.execute(stmt)
    tasks = list(result.scalars().all())

    # Aggregate counts
    by_priority = {"high": 0, "medium": 0, "low": 0}
    for t in tasks:
        if t.priority in by_priority:
            by_priority[t.priority] += 1
    return TaskListResponse(tasks=tasks, total=len(tasks), by_priority=by_priority)
