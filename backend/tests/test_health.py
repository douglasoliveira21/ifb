"""Testes para endpoints de health check."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Health check básico deve retornar status healthy."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "environment" in data


@pytest.mark.asyncio
async def test_health_check_response_format(client: AsyncClient):
    """Health check deve retornar todos os campos esperados."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert set(data.keys()) == {"status", "version", "environment"}
