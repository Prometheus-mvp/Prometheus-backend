"""Tests for RLS helper functions."""
import pytest
from unittest.mock import Mock, AsyncMock
from app.db.rls import set_user_context, verify_rls_enabled


@pytest.mark.asyncio
async def test_set_user_context():
    """Test set_user_context."""
    mock_session = AsyncMock()
    await set_user_context(mock_session, "user-123")
    # Currently a no-op, just ensure it doesn't raise


@pytest.mark.asyncio
async def test_verify_rls_enabled():
    """Test verify_rls_enabled checks RLS status."""
    mock_session = AsyncMock()
    mock_result = Mock()
    mock_result.fetchone.return_value = Mock(rowsecurity=True)
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    result = await verify_rls_enabled(mock_session, "users")
    assert result is True


@pytest.mark.asyncio
async def test_verify_rls_enabled_not_found():
    """Test verify_rls_enabled when table not found."""
    mock_session = AsyncMock()
    mock_result = Mock()
    mock_result.fetchone.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    result = await verify_rls_enabled(mock_session, "nonexistent")
    assert result is False

