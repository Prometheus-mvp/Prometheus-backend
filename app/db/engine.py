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
    database_url = (
        RAW_DATABASE_URL  # allow custom schemes; rely on caller to be correct
    )


def create_engine() -> AsyncEngine:
    """
    Create async SQLAlchemy engine with connection pooling.

    Returns:
        AsyncEngine instance configured for Supabase Postgres
    """
    # Use QueuePool for connection pooling in production
    # Use NullPool for testing or when connection pooling is handled externally
    poolclass = QueuePool if settings.is_production else NullPool

    # #region agent log
    import json

    with open(
        r"c:\Users\aroud\OneDrive\Documents\GitHub\Website\Prometheus-backend\.cursor\debug.log",
        "a",
    ) as f:
        f.write(
            json.dumps(
                {
                    "sessionId": "debug-session",
                    "runId": "pre-fix",
                    "hypothesisId": "A",
                    "location": "app/db/engine.py:32",
                    "message": "Pool class selection",
                    "data": {
                        "is_production": settings.is_production,
                        "poolclass": poolclass.__name__,
                    },
                    "timestamp": __import__("time").time() * 1000,
                }
            )
            + "\n"
        )
    # #endregion

    # Build engine kwargs - pool parameters only valid for QueuePool
    engine_kwargs = {
        "poolclass": poolclass,
        "echo": settings.is_development,  # Log SQL queries in development
    }

    # Only add pool parameters when using QueuePool (NullPool doesn't support them)
    if poolclass == QueuePool:
        engine_kwargs.update(
            {
                "pool_size": 10,  # Number of connections to maintain
                "max_overflow": 20,  # Additional connections beyond pool_size
                "pool_pre_ping": True,  # Verify connections before using
                "pool_recycle": 1800,  # recycle connections periodically to avoid stale sockets
            }
        )
        # #region agent log
        with open(
            r"c:\Users\aroud\OneDrive\Documents\GitHub\Website\Prometheus-backend\.cursor\debug.log",
            "a",
        ) as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "pre-fix",
                        "hypothesisId": "A",
                        "location": "app/db/engine.py:45",
                        "message": "Using QueuePool with pool parameters",
                        "data": {"pool_size": 10, "max_overflow": 20},
                        "timestamp": __import__("time").time() * 1000,
                    }
                )
                + "\n"
            )
        # #endregion
    else:
        # #region agent log
        with open(
            r"c:\Users\aroud\OneDrive\Documents\GitHub\Website\Prometheus-backend\.cursor\debug.log",
            "a",
        ) as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "pre-fix",
                        "hypothesisId": "A",
                        "location": "app/db/engine.py:50",
                        "message": "Using NullPool without pool parameters",
                        "data": {},
                        "timestamp": __import__("time").time() * 1000,
                    }
                )
                + "\n"
            )
        # #endregion

    engine = create_async_engine(database_url, **engine_kwargs)

    # #region agent log
    with open(
        r"c:\Users\aroud\OneDrive\Documents\GitHub\Website\Prometheus-backend\.cursor\debug.log",
        "a",
    ) as f:
        f.write(
            json.dumps(
                {
                    "sessionId": "debug-session",
                    "runId": "pre-fix",
                    "hypothesisId": "A",
                    "location": "app/db/engine.py:58",
                    "message": "Engine created successfully",
                    "data": {"poolclass": poolclass.__name__},
                    "timestamp": __import__("time").time() * 1000,
                }
            )
            + "\n"
        )
    # #endregion

    logger.info("Database engine created successfully")
    return engine


# Global engine instance
engine = create_engine()
