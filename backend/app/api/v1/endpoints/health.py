"""
Health Check Endpoint

Provides application and dependency health status.
Critical for container orchestration and load balancers.
"""

from typing import Dict, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.database.session import get_db


router = APIRouter()


@router.get(
    "/health",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
)
async def health_check(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        - Application status
        - Service information
        - Database connectivity
        - Environment info
        
    Used by:
        - Docker health checks
        - Kubernetes liveness/readiness probes
        - Load balancers
        - Monitoring systems
    """
    
    # Check database connectivity
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "unhealthy"
        logger.error("Database health check failed", error=str(e))
    
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": db_status,
    }


@router.get(
    "/health/ready",
    response_model=Dict[str, bool],
    status_code=status.HTTP_200_OK,
)
async def readiness_check(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, bool]:
    """
    Readiness probe endpoint.
    
    Returns whether the service is ready to accept traffic.
    Used by Kubernetes readiness probes.
    """
    
    try:
        await db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        return {"ready": False}


@router.get(
    "/health/live",
    response_model=Dict[str, bool],
    status_code=status.HTTP_200_OK,
)
async def liveness_check() -> Dict[str, bool]:
    """
    Liveness probe endpoint.
    
    Returns whether the service is alive.
    Used by Kubernetes liveness probes.
    """
    return {"alive": True}