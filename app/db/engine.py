"""SQLAlchemy async engine creation with connection pooling."""

import logging
from typing import Final

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings

logger = logging.getLogger(__name__)

# Normalize database URL for async usage
RAW_DATABASE_URL: Final[str] = settings.database_url
if RAW_DATABASE_URL.startswith("postgresql+asyncpg://"):
    database_url = RAW_DATABASE_URL
elif RAW_DATABASE_URL.startswith("postgresql://"):
    database_url = RAW_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    database_url = RAW_DATABASE_URL  # allow custom schemes; rely on caller to be correct


def create_engine() -> AsyncEngine:
    """
    Create async SQLAlchemy engine with connection pooling.

    Returns:
        AsyncEngine instance configured for Supabase Postgres
    """
    # Use QueuePool for connection pooling in production
    # Use NullPool for testing or when connection pooling is handled externally
    poolclass = QueuePool if settings.is_production else NullPool

    engine = create_async_engine(
        database_url,
        poolclass=poolclass,
        pool_size=10,  # Number of connections to maintain
        max_overflow=20,  # Additional connections beyond pool_size
        pool_pre_ping=True,  # Verify connections before using
        echo=settings.is_development,  # Log SQL queries in development
        pool_recycle=1800,  # recycle connections periodically to avoid stale sockets
    )

    logger.info("Database engine created successfully")
    return engine


# Global engine instance
engine = create_engine()
