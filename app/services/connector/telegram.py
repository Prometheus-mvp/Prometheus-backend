"""Telegram connector implementation (MTProto via Telethon)."""

import secrets
from typing import Any, Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

from app.core.config import settings
from app.services.connector.base import BaseConnector, TokenData
from app.models import LinkedAccount

logger = logging.getLogger(__name__)


class TelegramConnector(BaseConnector):
    """Telegram connector using Telethon (stubbed for structure)."""

    provider = "telegram"

    def __init__(self) -> None:
        super().__init__()

    async def build_auth_url(self, user_id: str) -> Tuple[str, str]:
        """Telegram uses phone auth; return placeholders."""
        state = secrets.token_urlsafe(16)
        return "telegram-phone-auth", state

    async def initiate_phone_auth(
        self, session: AsyncSession, user_id: str, phone_number: str
    ) -> Tuple[str, str]:
        """
        Initiate Telegram phone authentication.
        """
        auth_session_id = secrets.token_urlsafe(16)

        client = TelegramClient(
            StringSession(),
            settings.telegram_api_id,
            settings.telegram_api_hash,
        )
        await client.connect()
        try:
            send_result = await client.send_code_request(phone_number)
        except Exception as exc:
            logger.error("Telegram send_code_request failed", extra={"error": str(exc)})
            await client.disconnect()
            raise ValueError("Telegram code request failed") from exc
        await client.disconnect()
        phone_code_hash = send_result.phone_code_hash
        return auth_session_id, phone_code_hash

    async def verify_phone_code(
        self,
        session: AsyncSession,
        user_id: str,
        auth_session_id: str,
        phone_code: str,
        phone_code_hash: str,
        phone_number: Optional[str] = None,
    ):
        """
        Verify Telegram phone code.
        """
        if not phone_number:
            raise ValueError("phone_number is required for Telegram verification")

        client = TelegramClient(
            StringSession(),
            settings.telegram_api_id,
            settings.telegram_api_hash,
        )
        await client.connect()
        # sign in; this stores session in StringSession
        try:
            await client.sign_in(
                phone=phone_number,
                code=phone_code,
                phone_code_hash=phone_code_hash,
            )
        except PhoneCodeInvalidError as exc:
            await client.disconnect()
            raise ValueError("Invalid Telegram code") from exc
        except SessionPasswordNeededError as exc:
            await client.disconnect()
            raise ValueError(
                "Two-factor password required for Telegram account"
            ) from exc
        except Exception as exc:
            await client.disconnect()
            logger.error("Telegram sign_in failed", extra={"error": str(exc)})
            raise ValueError("Telegram verification failed") from exc
        session_str = client.session.save()
        await client.disconnect()

        token_data = TokenData(
            access_token=session_str,
            refresh_token=None,
            expires_in=None,
            scopes=None,
            token_type="bot",
        )

        account = await self._get_or_create_linked_account(
            session=session,
            user_id=user_id,
            provider_account_id=f"telegram-{user_id}",
            scopes=None,
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

    async def handle_callback(self, session: AsyncSession, user_id: str, **kwargs: Any):
        """Telegram does not use traditional OAuth callbacks; no-op."""
        return None

    async def fetch_events(
        self,
        session: AsyncSession,
        user_id: str,
        since: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch events from Telegram personal chats.
        """
        events: List[Dict[str, Any]] = []

        # Get linked account and token
        result = await session.execute(
            select(LinkedAccount).where(
                LinkedAccount.user_id == user_id,
                LinkedAccount.provider == self.provider,
            )
        )
        account = result.scalars().first()
        if not account:
            return events

        token_row = await self._latest_token(session, account.id)
        if not token_row:
            return events
        access_token, _ = self._decrypt_token(token_row)

        client = TelegramClient(
            StringSession(access_token),
            settings.telegram_api_id,
            settings.telegram_api_hash,
        )
        await client.connect()

        # Fetch last 50 messages from dialogs
        async for dialog in client.iter_dialogs(limit=5):
            async for message in client.iter_messages(dialog.id, limit=50):
                events.append(
                    {
                        "source": "telegram",
                        "source_account_id": account.id,
                        "external_id": str(message.id),
                        "thread_id": None,
                        "event_type": "message",
                        "title": None,
                        "body": message.message or "",
                        "url": None,
                        "text_for_embedding": message.message or "",
                        "content_hash": str(message.id),
                        "importance_score": 0,
                        "occurred_at": message.date,
                        "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
                        "raw": (
                            message.to_dict() if hasattr(message, "to_dict") else {}
                        ),
                    }
                )

        await client.disconnect()
        return events


telegram_connector = TelegramConnector()

__all__ = ["TelegramConnector", "telegram_connector"]
