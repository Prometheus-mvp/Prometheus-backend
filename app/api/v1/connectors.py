"""Connector API endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import delete, select

from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.models import LinkedAccount
from app.schemas.connector import (
    AccountStatus,
    LinkedAccountResponse,
    OAuthCallbackResponse,
    OAuthInitiateResponse,
    Provider,
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
logger = logging.getLogger(__name__)


@router.get("/slack/oauth/initiate", response_model=OAuthInitiateResponse)
async def slack_oauth_initiate(user_id: UserID) -> OAuthInitiateResponse:
    """Initiate Slack OAuth."""
    async def _operation():
        return await slack_connector.build_auth_url(user_id)
    
    auth_url, state = await handle_operation(
        db=None,
        operation=_operation,
        success_message="Slack OAuth initiated",
        error_message="Failed to initiate Slack OAuth",
        user_id=user_id,
        operation_name="slack_oauth_initiate",
        commit_on_success=False,
    )
    return OAuthInitiateResponse(auth_url=auth_url, state=state)


@router.get("/slack/oauth/callback", response_model=OAuthCallbackResponse)
async def slack_oauth_callback(
    db: DatabaseSession,
    user_id: UserID,
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="OAuth state parameter for CSRF protection"),
) -> OAuthCallbackResponse:
    """Handle Slack OAuth callback."""
    async def _operation():
        return await slack_connector.handle_callback(
            session=db, user_id=user_id, code=code, state=state
        )
    
    account = await handle_operation(
        db=db,
        operation=_operation,
        success_message="Slack OAuth callback successful",
        error_message="Slack OAuth callback failed",
        user_id=user_id,
        operation_name="slack_oauth_callback",
        commit_on_success=True,
    )
    
    return OAuthCallbackResponse(
        linked_account_id=account.id,
        provider=account.provider,
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
    async def _operation():
        return await telegram_connector.initiate_phone_auth(
            session=db, user_id=user_id, phone_number=payload.phone_number
        )
    
    auth_session_id, phone_code_hash = await handle_operation(
        db=db,
        operation=_operation,
        success_message="Telegram auth initiated",
        error_message="Failed to initiate Telegram authentication",
        user_id=user_id,
        operation_name="telegram_auth_initiate",
        commit_on_success=False,
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
    async def _operation():
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
        return account
    
    account = await handle_operation(
        db=db,
        operation=_operation,
        success_message="Telegram auth verified",
        error_message="Telegram verification failed",
        user_id=user_id,
        operation_name="telegram_auth_verify",
        commit_on_success=True,
    )
    
    return TelegramAuthVerifyResponse(
        linked_account_id=account.id,
        provider=account.provider,
        provider_account_id=account.provider_account_id,
        status=account.status,
    )


@router.get("/outlook/oauth/initiate", response_model=OAuthInitiateResponse)
async def outlook_oauth_initiate(user_id: UserID) -> OAuthInitiateResponse:
    """Initiate Outlook OAuth."""
    async def _operation():
        return await outlook_connector.build_auth_url(user_id)
    
    auth_url, state = await handle_operation(
        db=None,
        operation=_operation,
        success_message="Outlook OAuth initiated",
        error_message="Failed to initiate Outlook OAuth",
        user_id=user_id,
        operation_name="outlook_oauth_initiate",
        commit_on_success=False,
    )
    return OAuthInitiateResponse(auth_url=auth_url, state=state)


@router.get("/outlook/oauth/callback", response_model=OAuthCallbackResponse)
async def outlook_oauth_callback(
    db: DatabaseSession,
    user_id: UserID,
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="OAuth state parameter for CSRF protection"),
) -> OAuthCallbackResponse:
    """Handle Outlook OAuth callback."""
    async def _operation():
        return await outlook_connector.handle_callback(
            session=db, user_id=user_id, code=code, state=state
        )
    
    account = await handle_operation(
        db=db,
        operation=_operation,
        success_message="Outlook OAuth callback successful",
        error_message="Outlook OAuth callback failed",
        user_id=user_id,
        operation_name="outlook_oauth_callback",
        commit_on_success=True,
    )
    
    return OAuthCallbackResponse(
        linked_account_id=account.id,
        provider=account.provider,
        provider_account_id=account.provider_account_id,
        status=account.status,
    )


@router.get("", response_model=list[LinkedAccountResponse])
async def list_linked_accounts(
    db: DatabaseSession,
    user_id: UserID,
    provider: Provider | None = Query(
        default=None, description="Filter by provider (slack, telegram, outlook)"
    ),
    account_status: AccountStatus | None = Query(
        default=None, description="Filter by status (active, revoked, error)"
    ),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of accounts to return"),
    offset: int = Query(default=0, ge=0, description="Number of accounts to skip"),
) -> list[LinkedAccountResponse]:
    """List linked accounts for the current user."""
    stmt = (
        select(LinkedAccount)
        .where(LinkedAccount.user_id == user_id)
        .order_by(LinkedAccount.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if provider:
        stmt = stmt.where(LinkedAccount.provider == provider.value)
    if account_status:
        stmt = stmt.where(LinkedAccount.status == account_status.value)

    result = await db.execute(stmt)
    accounts = list(result.scalars().all())
    logger.debug("Listed linked accounts", extra={"user_id": user_id, "count": len(accounts)})
    return accounts


@router.delete("/{linked_account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_linked_account(
    linked_account_id: UUID,
    db: DatabaseSession,
    user_id: UserID,
) -> None:
    """Delete a linked account for the current user."""
    # Use RETURNING for better certainty
    stmt = (
        delete(LinkedAccount)
        .where(LinkedAccount.id == linked_account_id, LinkedAccount.user_id == user_id)
        .returning(LinkedAccount.id)
    )
    result = await db.execute(stmt)
    row = result.fetchone()
    
    if not row:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Linked account not found"
        )
    
    await db.commit()
    logger.info(
        "Deleted linked account",
        extra={"user_id": user_id, "account_id": str(linked_account_id)},
    )
