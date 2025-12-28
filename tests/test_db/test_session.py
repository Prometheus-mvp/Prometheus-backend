"""Tests for database session management."""
import pytest
from unittest.mock import Mock, AsyncMock, patch


@pytest.mark.asyncio
async def test_get_db_yields_session():
    """Test get_db yields a session."""
    from app.db.session import get_db
    
    with patch('app.db.session.AsyncSessionLocal') as mock_session_factory:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()
        mock_session_factory.return_value = mock_session
        
        async for session in get_db():
            assert session is not None
            break


@pytest.mark.asyncio
async def test_get_db_session():
    """Test get_db_session returns session."""
    from app.db.session import get_db_session
    
    with patch('app.db.session.AsyncSessionLocal') as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session
        
        session = await get_db_session()
        assert session == mock_session

