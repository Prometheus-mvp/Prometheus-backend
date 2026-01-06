"""Slack connector implementation."""

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


class SlackConnector(BaseConnector):
    """Slack OAuth connector."""

    provider = "slack"

    def __init__(self) -> None:
        super().__init__()
        self.base_auth_url = "https://slack.com/oauth/v2/authorize"

    async def build_auth_url(self, user_id: str) -> Tuple[str, str]:
        """Return Slack OAuth authorization URL and state."""
        state = secrets.token_urlsafe(16)
        scopes = "channels:history,channels:read,chat:write,users:read,users:read.email"
        auth_url = (
            f"{self.base_auth_url}"
            f"?client_id={settings.slack_client_id}"
            f"&redirect_uri={settings.slack_redirect_uri}"
            f"&scope={scopes}"
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
        Handle Slack OAuth callback.
        """
        try:
            token_resp = await self._client.post(
                "https://slack.com/api/oauth.v2.access",
                data={
                    "client_id": settings.slack_client_id,
                    "client_secret": settings.slack_client_secret,
                    "code": code,
                    "redirect_uri": settings.slack_redirect_uri,
                },
            )
            token_json = token_resp.json()
        except httpx.HTTPError as exc:
            logger.error("Slack OAuth HTTP error", extra={"error": str(exc)})
            raise ValueError("Slack OAuth failed") from exc

        if not token_json.get("ok"):
            logger.error("Slack OAuth failed", extra={"error": token_json})
            raise ValueError("Slack OAuth failed")

        authed_user = token_json.get("authed_user", {})
        provider_account_id = authed_user.get("id") or f"slack-{user_id}"
        scopes = token_json.get("scope")
        access_token = token_json.get("access_token")
        refresh_token = token_json.get("refresh_token")
        expires_in = token_json.get("expires_in")

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
            provider_account_id=provider_account_id,
            scopes=scopes,
            status="active",
            metadata={"team": token_json.get("team", {})},
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
        """Refresh Slack access token using stored refresh_token."""
        token_row = await self._latest_token(session, account.id)
        if not token_row or not token_row.refresh_token_enc:
            raise ValueError("No refresh token available")
        _, refresh = self._decrypt_token(token_row)
        if not refresh:
            raise ValueError("No refresh token available")

        try:
            resp = await self._client.post(
                "https://slack.com/api/oauth.v2.access",
                data={
                    "client_id": settings.slack_client_id,
                    "client_secret": settings.slack_client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh,
                },
            )
            data = resp.json()
        except httpx.HTTPError as exc:
            logger.error("Slack token refresh HTTP error", extra={"error": str(exc)})
            raise ValueError("Slack token refresh failed") from exc
        if not data.get("ok"):
            raise ValueError("Slack token refresh failed")

        token_data = TokenData(
            access_token=data.get("access_token"),
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
        """Get valid access token, refreshing if expired."""
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
        Fetch events from Slack.

        Uses conversations.history for public channels as an example.
        """
        events: List[Dict[str, Any]] = []

        # Fetch linked account and token
        result = await session.execute(
            select(LinkedAccount).where(
                LinkedAccount.user_id == user_id,
                LinkedAccount.provider == self.provider,
            )
        )
        account = result.scalars().first()
        if not account:
            return events

        try:
            access_token = await self._ensure_access_token(session, account)
        except Exception as exc:
            logger.warning("Slack access token unavailable", extra={"error": str(exc)})
            return events

        headers = {"Authorization": f"Bearer {access_token}"}
        # Fetch channels
        channel_resp = await self._client.get(
            "https://slack.com/api/conversations.list", headers=headers
        )
        channel_data = channel_resp.json()
        if not channel_data.get("ok"):
            logger.warning("Slack conversations.list failed", extra=channel_data)
            return events

        channels = channel_data.get("channels", [])
        for ch in channels:
            history_resp = await self._client.get(
                "https://slack.com/api/conversations.history",
                params={"channel": ch.get("id"), "limit": 50, "oldest": since or 0},
                headers=headers,
            )
            hist_json = history_resp.json()
            if not hist_json.get("ok"):
                continue
            for msg in hist_json.get("messages", []):
                events.append(
                    {
                        "source": "slack",
                        "source_account_id": account.id,
                        "external_id": msg.get("ts"),
                        "thread_id": None,
                        "event_type": "message",
                        "title": None,
                        "body": msg.get("text"),
                        "url": None,
                        "text_for_embedding": msg.get("text"),
                        "content_hash": msg.get("ts") or "",
                        "importance_score": 0,
                        "occurred_at": datetime.fromtimestamp(
                            float(msg.get("ts", "0")), tz=timezone.utc
                        ),
                        "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
                        "raw": msg,
                    }
                )

        return events


slack_connector = SlackConnector()

__all__ = ["SlackConnector", "slack_connector"]
