"""Helper functions for RLS policy enforcement and user context."""

import logging
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def set_user_context(session: AsyncSession, user_id: str) -> None:
    """
    Set Supabase RLS user context for the current session.

    Supabase RLS relies on request.jwt.claim.sub for auth.uid(). For service-role
    operations (background jobs, tests) we explicitly set it per connection.
    """
    if not user_id:
        raise ValueError("user_id is required to set RLS context")

    # SET LOCAL ensures the value only applies to the current transaction.
    await session.execute(
        text("SELECT set_config('request.jwt.claim.sub', :user_id, true)"),
        {"user_id": user_id},
    )


async def verify_rls_enabled(
    session: AsyncSession, table_name: str, schema: str = "public"
) -> bool:
    """
    Verify that RLS is enabled and at least one policy exists for the table.
    """
    query = text(
        """
        SELECT c.relrowsecurity AS rowsecurity, p.polname IS NOT NULL AS has_policy
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_policies p ON p.tablename = c.relname AND p.schemaname = n.nspname
        WHERE n.nspname = :schema AND c.relname = :table_name
        LIMIT 1
        """
    )
    result = await session.execute(query, {"schema": schema, "table_name": table_name})
    row = result.fetchone()
    if not row:
        return False
    return bool(row.rowsecurity and row.has_policy)


async def get_user_id_from_context(session: AsyncSession) -> Optional[str]:
    """
    Get user ID from current session context (if available).
    """
    result = await session.execute(
        text("SELECT current_setting('request.jwt.claim.sub', true)")
    )
    row = result.scalar_one_or_none()
    return row
