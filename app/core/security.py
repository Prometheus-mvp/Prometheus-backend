"""Security utilities for JWT validation and user authentication."""
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify Supabase JWT token and extract user information.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        Decoded JWT payload with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials

    try:
        # Verify token with Supabase anon key
        # Supabase uses HS256 algorithm with the anon key as secret
        payload = jwt.decode(
            token,
            settings.supabase_anon_key,
            algorithms=["HS256"],
            audience="authenticated",
        )

        # Extract user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "raw_payload": payload,
        }

    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token_data: dict = Depends(verify_token)) -> dict:
    """
    Get current authenticated user from token.

    Args:
        token_data: Decoded token data from verify_token

    Returns:
        User information dictionary
    """
    return token_data


def extract_user_id(token_data: dict) -> str:
    """
    Extract user ID from token data.

    Args:
        token_data: Decoded token data

    Returns:
        User ID (UUID string)
    """
    return token_data["user_id"]

