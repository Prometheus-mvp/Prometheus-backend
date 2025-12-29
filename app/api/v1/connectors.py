"""Connector API endpoints."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import delete, select

from app.api.deps import DatabaseSession, UserID
from app.models import LinkedAccount
from app.schemas.connector import (
    LinkedAccountResponse,
    OAuthCallbackResponse,
    OAuthInitiateResponse,
    TelegramAuthInitiateRequest,
    TelegramAuthInitiateResponse,
    TelegramAuthVerifyRequest,
    TelegramAuthVerifyResponse,
)
from app.services.connector import (
    outlook_connector,
    slack_connector,
    telegram_connector,
)

router = APIRouter(prefix="/connectors", tags=["connectors"])


@router.get("/slack/oauth/initiate", response_model=OAuthInitiateResponse)
async def slack_oauth_initiate(user_id: UserID) -> OAuthInitiateResponse:
    """Initiate Slack OAuth."""
    auth_url, state = await slack_connector.build_auth_url(user_id)
    return OAuthInitiateResponse(auth_url=auth_url, state=state)


@router.get("/slack/oauth/callback", response_model=OAuthCallbackResponse)
async def slack_oauth_callback(
    code: str,
    state: str,
    db: DatabaseSession,
    user_id: UserID,
) -> OAuthCallbackResponse:
    """Handle Slack OAuth callback."""
    account = await slack_connector.handle_callback(
        session=db, user_id=user_id, code=code, state=state
    )
    return OAuthCallbackResponse(
        linked_account_id=account.id,
        provider="slack",
        provider_account_id=account.provider_account_id,
        status=account.status,
    )


@router.post(
    "/telegram/auth/initiate",
    response_model=TelegramAuthInitiateResponse,
)
async def telegram_auth_initiate(
    payload: TelegramAuthInitiateRequest,
    db: DatabaseSession,
    user_id: UserID,
) -> TelegramAuthInitiateResponse:
    """Initiate Telegram phone authentication."""
    auth_session_id, phone_code_hash = await telegram_connector.initiate_phone_auth(
        session=db, user_id=user_id, phone_number=payload.phone_number
    )
    return TelegramAuthInitiateResponse(
        auth_session_id=auth_session_id,
        phone_code_hash=phone_code_hash,
    )


@router.post(
    "/telegram/auth/verify",
    response_model=TelegramAuthVerifyResponse,
)
async def telegram_auth_verify(
    payload: TelegramAuthVerifyRequest,
    db: DatabaseSession,
    user_id: UserID,
) -> TelegramAuthVerifyResponse:
    """Verify Telegram phone code."""
    account = await telegram_connector.verify_phone_code(
        session=db,
        user_id=user_id,
        auth_session_id=str(payload.auth_session_id),
        phone_code=payload.phone_code,
        phone_code_hash=payload.phone_code_hash,
        phone_number=payload.phone_number,
    )
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram verification failed",
        )
    return TelegramAuthVerifyResponse(
        linked_account_id=account.id,
        provider="telegram",
        provider_account_id=account.provider_account_id,
        status=account.status,
    )


@router.get("/outlook/oauth/initiate", response_model=OAuthInitiateResponse)
async def outlook_oauth_initiate(user_id: UserID) -> OAuthInitiateResponse:
    """Initiate Outlook OAuth."""
    auth_url, state = await outlook_connector.build_auth_url(user_id)
    return OAuthInitiateResponse(auth_url=auth_url, state=state)


@router.get("/outlook/oauth/callback", response_model=OAuthCallbackResponse)
async def outlook_oauth_callback(
    code: str,
    state: str,
    db: DatabaseSession,
    user_id: UserID,
) -> OAuthCallbackResponse:
    """Handle Outlook OAuth callback."""
    account = await outlook_connector.handle_callback(
        session=db, user_id=user_id, code=code, state=state
    )
    return OAuthCallbackResponse(
        linked_account_id=account.id,
        provider="outlook",
        provider_account_id=account.provider_account_id,
        status=account.status,
    )


@router.get("", response_model=list[LinkedAccountResponse])
async def list_linked_accounts(
    db: DatabaseSession, user_id: UserID
) -> list[LinkedAccountResponse]:
    """List linked accounts for the current user."""
    result = await db.execute(
        select(LinkedAccount).where(LinkedAccount.user_id == user_id)
    )
    return list(result.scalars().all())


@router.delete("/{linked_account_id}", status_code=204)
async def delete_linked_account(
    linked_account_id: str,
    db: DatabaseSession,
    user_id: UserID,
) -> None:
    """Delete a linked account for the current user."""
    stmt = delete(LinkedAccount).where(
        LinkedAccount.id == linked_account_id, LinkedAccount.user_id == user_id
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Linked account not found")
    return None
