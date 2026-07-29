"""
Health Endpoint Tests

Tests the health check endpoints for proper responses.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test basic health check endpoint."""
    response = await client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert data["service"] == "MedVision AI"
    assert "version" in data
    assert "environment" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient):
    """Test readiness probe endpoint."""
    response = await client.get("/api/v1/health/ready")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "ready" in data
    assert isinstance(data["ready"], bool)


@pytest.mark.asyncio
async def test_liveness_check(client: AsyncClient):
    """Test liveness probe endpoint."""
    response = await client.get("/api/v1/health/live")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["alive"] is True