"""Outlook connector implementation (Microsoft Graph)."""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import LinkedAccount
from app.services.connector.base import BaseConnector, TokenData

logger = logging.getLogger(__name__)


class OutlookConnector(BaseConnector):
    """Microsoft Outlook (Graph) connector."""

    provider = "outlook"

    def __init__(self) -> None:
        super().__init__()
        self.base_auth_url = (
            "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
        )
        self.token_url = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"

    async def build_auth_url(self, user_id: str) -> Tuple[str, str]:
        """Return Outlook OAuth authorization URL and state."""
        state = secrets.token_urlsafe(16)
        tenant = settings.outlook_tenant_id or "common"
        scopes = "offline_access Calendars.Read Mail.Read"
        auth_url = (
            f"{self.base_auth_url.format(tenant=tenant)}"
            f"?client_id={settings.outlook_client_id}"
            f"&response_type=code"
            f"&redirect_uri={settings.outlook_redirect_uri}"
            f"&response_mode=query"
            f"&scope={scopes.replace(' ', '%20')}"
            f"&state={state}"
        )
        return auth_url, state

    async def handle_callback(
        self,
        session: AsyncSession,
        user_id: str,
        code: str,
        state: str,
    ):
        """
        Handle Outlook OAuth callback.
        """
        tenant = settings.outlook_tenant_id or "common"
        try:
            token_resp = await self._client.post(
                self.token_url.format(tenant=tenant),
                data={
                    "client_id": settings.outlook_client_id,
                    "client_secret": settings.outlook_client_secret,
                    "code": code,
                    "redirect_uri": settings.outlook_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            token_json = token_resp.json()
        except httpx.HTTPError as exc:
            logger.error("Outlook OAuth HTTP error", extra={"error": str(exc)})
            raise ValueError("Outlook OAuth failed") from exc
        access_token = token_json.get("access_token")
        refresh_token = token_json.get("refresh_token")
        expires_in = token_json.get("expires_in")
        scopes = token_json.get("scope")

        if not access_token:
            logger.error("Outlook OAuth failed", extra={"resp": token_json})
            raise ValueError("Outlook OAuth failed")

        token_data = TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            scopes=scopes,
            token_type="bearer",
        )

        account = await self._get_or_create_linked_account(
            session=session,
            user_id=user_id,
            provider_account_id=f"outlook-{user_id}",
            scopes=token_data.scopes,
            status="active",
            metadata={},
        )

        await self._store_tokens(
            session=session,
            user_id=user_id,
            linked_account_id=account.id,
            token_data=token_data,
        )
        return account

    async def _refresh_access_token(
        self, session: AsyncSession, account: LinkedAccount
    ) -> str:
        token_row = await self._latest_token(session, account.id)
        if not token_row or not token_row.refresh_token_enc:
            raise ValueError("No refresh token available")
        _, refresh = self._decrypt_token(token_row)
        if not refresh:
            raise ValueError("No refresh token available")

        tenant = settings.outlook_tenant_id or "common"
        try:
            resp = await self._client.post(
                self.token_url.format(tenant=tenant),
                data={
                    "client_id": settings.outlook_client_id,
                    "client_secret": settings.outlook_client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh,
                    "redirect_uri": settings.outlook_redirect_uri,
                },
            )
            data = resp.json()
        except httpx.HTTPError as exc:
            logger.error("Outlook token refresh HTTP error", extra={"error": str(exc)})
            raise ValueError("Outlook token refresh failed") from exc
        access_token = data.get("access_token")
        if not access_token:
            raise ValueError("Outlook token refresh failed")
        token_data = TokenData(
            access_token=access_token,
            refresh_token=data.get("refresh_token", refresh),
            expires_in=data.get("expires_in"),
            scopes=data.get("scope"),
            token_type="bearer",
        )
        await self._store_tokens(
            session=session,
            user_id=account.user_id,
            linked_account_id=account.id,
            token_data=token_data,
        )
        return token_data.access_token

    async def _ensure_access_token(
        self, session: AsyncSession, account: LinkedAccount
    ) -> str:
        token_row = await self._latest_token(session, account.id)
        if not token_row:
            raise ValueError("No token found")
        access, _ = self._decrypt_token(token_row)
        if token_row.expires_at and token_row.expires_at < datetime.now(timezone.utc):
            return await self._refresh_access_token(session, account)
        return access

    async def fetch_events(
        self,
        session: AsyncSession,
        user_id: str,
        since: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch events from Outlook (mail/calendar).
        """
        events: List[Dict[str, Any]] = []

        # Get linked account and token
        result = await session.execute(
            LinkedAccount.__table__.select().where(
                LinkedAccount.user_id == user_id,
                LinkedAccount.provider == self.provider,
            )
        )
        account = result.fetchone()
        if not account:
            return events

        try:
            access_token = await self._ensure_access_token(session, account)
        except Exception as exc:
            logger.warning(
                "Outlook access token unavailable", extra={"error": str(exc)}
            )
            return events
        headers = {"Authorization": f"Bearer {access_token}"}

        # Fetch calendar events as example
        calendar_resp = await self._client.get(
            "https://graph.microsoft.com/v1.0/me/events",
            params={"$top": 50},
            headers=headers,
        )
        data = calendar_resp.json()
        items = data.get("value", [])
        for item in items:
            start_raw = item.get("start", {}).get("dateTime")
            try:
                start_dt = (
                    datetime.fromisoformat(start_raw)
                    if start_raw
                    else datetime.now(timezone.utc)
                )
            except Exception:
                start_dt = datetime.now(timezone.utc)
            events.append(
                {
                    "source": "outlook",
                    "source_account_id": account.id,
                    "external_id": item.get("id"),
                    "thread_id": None,
                    "event_type": "calendar",
                    "title": item.get("subject"),
                    "body": item.get("bodyPreview"),
                    "url": item.get("webLink"),
                    "text_for_embedding": item.get("bodyPreview"),
                    "content_hash": item.get("id") or "",
                    "importance_score": 0,
                    "occurred_at": start_dt,
                    "expires_at": start_dt + timedelta(days=30),
                    "raw": item,
                }
            )

        return events


outlook_connector = OutlookConnector()

__all__ = ["OutlookConnector", "outlook_connector"]
