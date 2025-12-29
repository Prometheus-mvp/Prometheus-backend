"""Pydantic schemas."""

from app.schemas.calendar import (
    CalendarEventBase,
    CalendarEventCreate,
    CalendarEventListResponse,
    CalendarEventResponse,
    CalendarEventUpdate,
)
from app.schemas.connector import (
    LinkedAccountBase,
    LinkedAccountCreate,
    LinkedAccountResponse,
    OAuthCallbackRequest,
    OAuthCallbackResponse,
    OAuthInitiateResponse,
    TelegramAuthInitiateRequest,
    TelegramAuthInitiateResponse,
    TelegramAuthVerifyRequest,
    TelegramAuthVerifyResponse,
)
from app.schemas.event import EventBase, EventCreate, EventResponse
from app.schemas.summary import SummaryBase, SummaryCreate, SummaryResponse
from app.schemas.task import (
    TaskBase,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.schemas.user import UserBase, UserCreate, UserResponse, UserUpdate

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "LinkedAccountBase",
    "LinkedAccountCreate",
    "LinkedAccountResponse",
    "OAuthInitiateResponse",
    "OAuthCallbackRequest",
    "OAuthCallbackResponse",
    "TelegramAuthInitiateRequest",
    "TelegramAuthInitiateResponse",
    "TelegramAuthVerifyRequest",
    "TelegramAuthVerifyResponse",
    "EventBase",
    "EventCreate",
    "EventResponse",
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "CalendarEventBase",
    "CalendarEventCreate",
    "CalendarEventUpdate",
    "CalendarEventResponse",
    "CalendarEventListResponse",
    "SummaryBase",
    "SummaryCreate",
    "SummaryResponse",
]
