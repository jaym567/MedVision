"""
API v1 Router

Aggregates all API v1 endpoints.
Future endpoints (auth, studies, models, reports) will be added here.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health


api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    tags=["Health"],
)

# Future routers will be added here:
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(studies.router, prefix="/studies", tags=["Studies"])
# api_router.include_router(models.router, prefix="/models", tags=["AI Models"])
# api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])