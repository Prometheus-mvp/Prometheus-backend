"""API v1 router."""
from fastapi import APIRouter

from app.api.v1 import calendar, connectors, prompts, tasks

api_router = APIRouter()

# Connectors
api_router.include_router(connectors.router, prefix="/connectors")
# Prompts
api_router.include_router(prompts.router, prefix="")
# Tasks
api_router.include_router(tasks.router, prefix="")
# Calendar
api_router.include_router(calendar.router, prefix="")

__all__ = ["api_router"]

