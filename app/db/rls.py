"""Helper functions for RLS policy enforcement and user context."""
import logging
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def set_user_context(session: AsyncSession, user_id: str) -> None:
    """
    Set Supabase RLS user context for the current session.

    This function sets the auth.uid() function in Supabase to the provided user_id,
    enabling Row Level Security policies to work correctly.

    Args:
        session: Database session
        user_id: User UUID string
    """
    # In Supabase, RLS policies use auth.uid() which is automatically set from JWT
    # However, for service role operations or testing, we may need to set it manually
    # This is typically done via SET LOCAL or by using the service role key
    # For most operations, Supabase handles this automatically via JWT

    # For direct database operations (e.g., background jobs), we might need:
    # await session.execute(text(f"SET LOCAL request.jwt.claim.sub = '{user_id}'"))
    # But this is usually handled by Supabase's connection pooling and JWT

    # For now, we'll rely on Supabase's automatic RLS enforcement via JWT
    # This function is a placeholder for future service role operations
    pass


async def verify_rls_enabled(session: AsyncSession, table_name: str) -> bool:
    """
    Verify that RLS is enabled on a table.

    Args:
        session: Database session
        table_name: Name of the table to check

    Returns:
        True if RLS is enabled, False otherwise
    """
    query = text("""
        SELECT tablename, rowsecurity
        FROM pg_tables
        WHERE schemaname = 'public' AND tablename = :table_name
    """)
    result = await session.execute(query, {"table_name": table_name})
    row = result.fetchone()

    if row:
        return bool(row.rowsecurity)
    return False


async def get_user_id_from_context(session: AsyncSession) -> Optional[str]:
    """
    Get user ID from current session context (if available).

    Args:
        session: Database session

    Returns:
        User ID string or None if not available
    """
    # This would extract user_id from Supabase's JWT context
    # In practice, Supabase handles this automatically via RLS
    # This is a placeholder for service role operations
    return None

