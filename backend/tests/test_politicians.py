"""Testes para endpoints de políticos."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_politicians_public(client: AsyncClient):
    """Lista de políticos deve retornar 200."""
    response = await client.get("/api/v1/politicians")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


@pytest.mark.asyncio
async def test_list_politicians_with_query(client: AsyncClient):
    """Pesquisa deve aceitar parâmetro q."""
    response = await client.get("/api/v1/politicians?q=silva")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_politicians_with_state_filter(client: AsyncClient):
    """Filtro por estado deve funcionar."""
    response = await client.get("/api/v1/politicians?state=SP")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_politician_not_found(client: AsyncClient):
    """Político inexistente deve retornar 404."""
    response = await client.get("/api/v1/politicians/slug-inexistente")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_politicians_unauthorized(client: AsyncClient):
    """Admin sem auth deve retornar 401."""
    response = await client.get("/api/v1/admin/politicians")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_politician_unauthorized(client: AsyncClient):
    """Criar político sem auth deve retornar 401."""
    response = await client.post("/api/v1/admin/politicians", json={
        "full_name": "Teste da Silva",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_pagination_limits(client: AsyncClient):
    """Paginação deve respeitar limites."""
    response = await client.get("/api/v1/politicians?page=1&limit=50")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 50


@pytest.mark.asyncio
async def test_pagination_max_limit(client: AsyncClient):
    """Limite máximo de 100 deve ser respeitado."""
    response = await client.get("/api/v1/politicians?limit=200")
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_politician_sources_not_found(client: AsyncClient):
    """Fontes de político inexistente deve retornar 404."""
    response = await client.get("/api/v1/politicians/nao-existe/sources")
    assert response.status_code == 404
