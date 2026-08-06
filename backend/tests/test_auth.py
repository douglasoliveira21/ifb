"""Testes para o módulo de autenticação."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Cadastro válido deve retornar 201."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "senhasegura123",
        "full_name": "Usuário Teste",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Usuário Teste"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    """Senha curta deve retornar erro."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "test2@example.com",
        "password": "short",
        "full_name": "Usuário",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """E-mail inválido deve retornar erro."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "not-an-email",
        "password": "senhasegura123",
        "full_name": "Usuário",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Login com credenciais inválidas deve retornar 401 genérico."""
    response = await client.post("/api/v1/auth/login", json={
        "email": "nobody@example.com",
        "password": "wrongpassword1",
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Credenciais inválidas."


@pytest.mark.asyncio
async def test_forgot_password_generic_response(client: AsyncClient):
    """Recuperação de senha deve retornar mensagem genérica."""
    response = await client.post("/api/v1/auth/forgot-password", json={
        "email": "nonexistent@example.com",
    })
    assert response.status_code == 200
    data = response.json()
    assert "instruções serão enviadas" in data["message"]


@pytest.mark.asyncio
async def test_resend_verification_generic_response(client: AsyncClient):
    """Reenvio de verificação deve retornar mensagem genérica."""
    response = await client.post("/api/v1/auth/resend-verification", json={
        "email": "nonexistent@example.com",
    })
    assert response.status_code == 200
    data = response.json()
    assert "instruções serão enviadas" in data["message"]


@pytest.mark.asyncio
async def test_verify_email_invalid_token(client: AsyncClient):
    """Token de verificação inválido deve retornar erro."""
    response = await client.post("/api/v1/auth/verify-email", json={
        "token": "invalid-token-here",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: AsyncClient):
    """Token de reset inválido deve retornar erro."""
    response = await client.post("/api/v1/auth/reset-password", json={
        "token": "invalid-token",
        "new_password": "novasenha1234",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """Acessar /users/me sem autenticação deve retornar 401."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_sessions_unauthenticated(client: AsyncClient):
    """Acessar sessões sem autenticação deve retornar 401."""
    response = await client.get("/api/v1/auth/sessions")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_roles_unauthorized(client: AsyncClient):
    """Acessar admin sem role deve retornar 401."""
    response = await client.get("/api/v1/admin/roles")
    assert response.status_code == 401
