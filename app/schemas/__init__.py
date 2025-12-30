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
from app.schemas.note import NoteBase, NoteCreate, NoteResponse, NoteUpdate
from app.schemas.thread import ThreadBase, ThreadCreate, ThreadResponse, ThreadUpdate
from app.schemas.entity import EntityBase, EntityCreate, EntityResponse, EntityUpdate
from app.schemas.draft import DraftBase, DraftCreate, DraftResponse, DraftUpdate
from app.schemas.proposal import (
    ProposalBase,
    ProposalCreate,
    ProposalResponse,
    ProposalUpdate,
)
from app.schemas.prompt import PromptRequest, PromptResponse

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "LinkedAccountBase",
    "LinkedAccountResponse",
    "OAuthInitiateResponse",
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
    "NoteBase",
    "NoteCreate",
    "NoteUpdate",
    "NoteResponse",
    "ThreadBase",
    "ThreadCreate",
    "ThreadUpdate",
    "ThreadResponse",
    "EntityBase",
    "EntityCreate",
    "EntityUpdate",
    "EntityResponse",
    "DraftBase",
    "DraftCreate",
    "DraftUpdate",
    "DraftResponse",
    "ProposalBase",
    "ProposalCreate",
    "ProposalUpdate",
    "ProposalResponse",
    "PromptRequest",
    "PromptResponse",
]
