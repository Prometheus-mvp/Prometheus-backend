"""FastAPI dependencies for authentication and database session."""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import extract_user_id, get_current_user
from app.db.session import get_db


# Database session dependency
async def get_db_session() -> AsyncSession:
    """Get database session dependency."""
    async for session in get_db():
        yield session


# User authentication dependency
async def get_current_user_dep():
    """Get current authenticated user dependency."""
    return await get_current_user()


# User ID extraction
def get_user_id(user_data: dict = Depends(get_current_user_dep)) -> str:
    """Extract user ID from authenticated user data."""
    return extract_user_id(user_data)


# Type aliases for dependency injection
DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[dict, Depends(get_current_user_dep)]
UserID = Annotated[str, Depends(get_user_id)]

