"""Base connector interface and common utilities."""
import secrets
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import encryption_service
from app.models import LinkedAccount, OAuthToken


class TokenData:
    """Container for OAuth token payloads."""

    def __init__(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None,
        scopes: Optional[str] = None,
        token_type: str = "bearer",
    ) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.scopes = scopes
        self.token_type = token_type

    def expires_at(self) -> Optional[datetime]:
        """Return absolute expiry time in UTC if provided."""
        if self.expires_in is None:
            return None
        return datetime.now(timezone.utc) + timedelta(seconds=self.expires_in)


class BaseConnector(ABC):
    """Abstract connector interface."""

    provider: str
    http_timeout: float = 10.0

    def __init__(self) -> None:
        self.state = secrets.token_urlsafe(16)
        self._client = httpx.AsyncClient(timeout=self.http_timeout)

    @abstractmethod
    async def build_auth_url(self, user_id: str) -> Tuple[str, str]:
        """Return (auth_url, state)."""

    @abstractmethod
    async def handle_callback(
        self, session: AsyncSession, user_id: str, **kwargs: Any
    ) -> LinkedAccount:
        """Handle OAuth callback and persist credentials."""

    @abstractmethod
    async def fetch_events(
        self,
        session: AsyncSession,
        user_id: str,
        since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch new events for a user."""

    async def _get_or_create_linked_account(
        self,
        session: AsyncSession,
        user_id: str,
        provider_account_id: str,
        scopes: Optional[str] = None,
        status: str = "active",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LinkedAccount:
        """Fetch an existing linked account or create a new one."""
        metadata = metadata or {}
        result = await session.execute(
            select(LinkedAccount).where(
                LinkedAccount.user_id == user_id,
                LinkedAccount.provider == self.provider,
                LinkedAccount.provider_account_id == provider_account_id,
            )
        )
        account = result.scalars().first()
        if account:
            # Update scopes/status if changed
            account.scopes = scopes
            account.status = status
            account.metadata = metadata
            await session.flush()
            return account

        account = LinkedAccount(
            user_id=user_id,
            provider=self.provider,
            provider_account_id=provider_account_id,
            scopes=scopes,
            status=status,
            metadata=metadata,
        )
        session.add(account)
        await session.flush()
        return account

    async def _latest_token(
        self, session: AsyncSession, linked_account_id: str
    ) -> Optional[OAuthToken]:
        """Return the most recent non-revoked token for a linked account."""
        result = await session.execute(
            select(OAuthToken)
            .where(OAuthToken.linked_account_id == linked_account_id)
            .order_by(desc(OAuthToken.created_at))
        )
        return result.scalars().first()

    def _decrypt_token(self, token: OAuthToken) -> Tuple[str, Optional[str]]:
        """Decrypt access/refresh tokens."""
        access = (
            encryption_service.decrypt(token.access_token_enc)
            if token.access_token_enc
            else ""
        )
        refresh = (
            encryption_service.decrypt(token.refresh_token_enc)
            if token.refresh_token_enc
            else None
        )
        return access, refresh

    async def _store_tokens(
        self,
        session: AsyncSession,
        user_id: str,
        linked_account_id: str,
        token_data: TokenData,
    ) -> OAuthToken:
        """Encrypt and store OAuth tokens."""
        access_enc = encryption_service.encrypt(token_data.access_token)
        refresh_enc = (
            encryption_service.encrypt(token_data.refresh_token)
            if token_data.refresh_token
            else None
        )

        expires_at = token_data.expires_at()
        token = OAuthToken(
            user_id=user_id,
            linked_account_id=linked_account_id,
            token_type=token_data.token_type,
            scopes=token_data.scopes,
            access_token_enc=access_enc,
            refresh_token_enc=refresh_enc,
            expires_at=expires_at,
            token_fingerprint=encryption_service.generate_token_fingerprint(
                token_data.access_token
            ),
        )
        session.add(token)
        await session.flush()
        return token


__all__ = ["BaseConnector", "TokenData"]

