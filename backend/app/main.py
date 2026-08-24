"""
MedVision AI - Backend Application Entry Point

Production-quality FastAPI application with:
- Health monitoring
- CORS configuration
- API versioning
- Lifecycle management
- Error handling
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Connection pool management
    - Resource cleanup

    Note: Database schema is managed via Alembic migrations.
    Do NOT run create_all here — it conflicts with existing indexes.
    """
    # Startup
    logger.info("Starting MedVision AI Backend", environment=settings.APP_ENV)
    logger.info("Database schema managed by Alembic migrations")

    yield

    # Shutdown
    logger.info("Shutting down MedVision AI Backend")
    await engine.dispose()


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered medical imaging workstation",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Setup logging
setup_logging(settings.LOG_LEVEL)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    
    In production, this would integrate with Sentry or similar.
    """
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_error",
        },
    )


@app.get("/")
async def root():
    """Root endpoint - redirects to API documentation."""
    return {
        "message": "MedVision AI Backend",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )