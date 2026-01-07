"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import get_uvicorn_log_config, setup_logging

# Patch uvicorn's default log_config to prevent reload errors
# This ensures uvicorn has a valid log_config when run from command line
try:
    import uvicorn.config
    # Override uvicorn's default log_config with our minimal config
    uvicorn.config.LOGGING_CONFIG = get_uvicorn_log_config()
except (ImportError, AttributeError):
    # If uvicorn isn't available or structure changed, continue without patching
    pass

# Setup logging
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Prometheus v1 Backend API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Log level: {settings.log_level}")
    yield
    # Shutdown
    logger.info("Shutting down Prometheus v1 Backend API")


# Create FastAPI app
app = FastAPI(
    title="Prometheus v1 Backend API",
    description="Production-grade backend for Prometheus v1",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    # Configure allowed origins in production
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0",
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Prometheus v1 Backend API",
        "version": "1.0.0",
        "docs": "/docs",
    }


app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    from app.core.logging import get_uvicorn_log_config

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_config=get_uvicorn_log_config(),  # Provide minimal log_config for uvicorn compatibility
    )
