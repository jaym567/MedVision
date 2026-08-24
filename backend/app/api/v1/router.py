# backend/app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, studies

api_router = APIRouter()

# Health check endpoint
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Studies endpoints
api_router.include_router(
    studies.router,
    prefix="/studies",
    tags=["Studies"]
)
