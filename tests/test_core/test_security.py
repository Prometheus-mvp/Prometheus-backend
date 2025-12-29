"""Tests for app.core.security module."""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from app.core.security import verify_token, get_current_user, extract_user_id


@pytest.mark.asyncio
async def test_verify_token_success():
    """Test successful token verification."""
    mock_credentials = Mock()
    mock_credentials.credentials = "valid_token"

    with patch("app.core.security.jwt.decode") as mock_decode:
        mock_decode.return_value = {
            "sub": "user-123",
            "email": "test@example.com",
        }

        result = await verify_token(mock_credentials)

        assert result["user_id"] == "user-123"
        assert result["email"] == "test@example.com"
        assert "raw_payload" in result


@pytest.mark.asyncio
async def test_verify_token_missing_user_id():
    """Test token verification fails when user_id is missing."""
    mock_credentials = Mock()
    mock_credentials.credentials = "invalid_token"

    with patch("app.core.security.jwt.decode") as mock_decode:
        mock_decode.return_value = {"email": "test@example.com"}

        with pytest.raises(HTTPException) as exc_info:
            await verify_token(mock_credentials)

        assert exc_info.value.status_code == 401
        assert "missing user ID" in exc_info.value.detail


@pytest.mark.asyncio
async def test_verify_token_jwt_error():
    """Test token verification handles JWT errors."""
    mock_credentials = Mock()
    mock_credentials.credentials = "malformed_token"

    with patch("app.core.security.jwt.decode") as mock_decode:
        from jose import JWTError

        mock_decode.side_effect = JWTError("Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            await verify_token(mock_credentials)

        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user():
    """Test get_current_user returns token data."""
    token_data = {"user_id": "user-123", "email": "test@example.com"}

    with patch("app.core.security.verify_token", return_value=token_data):
        result = await get_current_user()
        assert result == token_data


def test_extract_user_id():
    """Test extract_user_id extracts user ID from token data."""
    token_data = {"user_id": "user-456", "email": "test@example.com"}
    result = extract_user_id(token_data)
    assert result == "user-456"
