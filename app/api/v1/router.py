"""API v1 router."""

from fastapi import APIRouter

from app.api.v1 import (
    calendar,
    connectors,
    drafts,
    entities,
    events,
    notes,
    proposals,
    prompts,
    summaries,
    tasks,
    threads,
    users,
)

api_router = APIRouter()

# Users
api_router.include_router(users.router, prefix="")
# Connectors
api_router.include_router(connectors.router, prefix="/connectors")
# Prompts
api_router.include_router(prompts.router, prefix="")
# Tasks
api_router.include_router(tasks.router, prefix="")
# Calendar
api_router.include_router(calendar.router, prefix="")
# Events
api_router.include_router(events.router, prefix="")
# Summaries
api_router.include_router(summaries.router, prefix="")
# Notes
api_router.include_router(notes.router, prefix="")
# Threads
api_router.include_router(threads.router, prefix="")
# Entities
api_router.include_router(entities.router, prefix="")
# Drafts
api_router.include_router(drafts.router, prefix="")
# Proposals
api_router.include_router(proposals.router, prefix="")

__all__ = ["api_router"]
