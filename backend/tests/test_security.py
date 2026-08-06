"""Testes unitários para o módulo de segurança."""

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_secure_token,
    hash_password,
    hash_token,
    validate_password_strength,
    verify_password,
    verify_token_hash,
)


def test_hash_and_verify_password():
    """Hash e verificação de senha devem funcionar corretamente."""
    password = "minha_senha_segura"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("senha_errada", hashed) is False


def test_password_hash_is_argon2id():
    """Hash deve usar Argon2id."""
    hashed = hash_password("testpassword")
    assert hashed.startswith("$argon2id$")


def test_access_token_creation_and_decode():
    """Access token deve ser criado e decodificado corretamente."""
    token = create_access_token(subject="user-123")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
    assert "jti" in payload
    assert "exp" in payload
    assert "iat" in payload


def test_refresh_token_creation():
    """Refresh token deve retornar token e family."""
    token, family = create_refresh_token(subject="user-456")
    assert token
    assert family
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user-456"
    assert payload["type"] == "refresh"
    assert payload["family"] == family


def test_decode_invalid_token():
    """Token inválido deve retornar None."""
    assert decode_token("invalid.token.here") is None
    assert decode_token("") is None


def test_secure_token_generation():
    """Tokens seguros devem ser únicos e suficientemente longos."""
    t1 = generate_secure_token()
    t2 = generate_secure_token()
    assert t1 != t2
    assert len(t1) >= 32


def test_token_hash_and_verify():
    """Hash de token e verificação devem funcionar."""
    token = "my-secret-token"
    h = hash_token(token)
    assert h != token
    assert verify_token_hash(token, h) is True
    assert verify_token_hash("wrong-token", h) is False


def test_password_validation_too_short():
    """Senha muito curta deve falhar."""
    errors = validate_password_strength("short")
    assert len(errors) > 0
    assert "mínimo" in errors[0]


def test_password_validation_too_long():
    """Senha muito longa deve falhar."""
    errors = validate_password_strength("a" * 200)
    assert len(errors) > 0
    assert "máximo" in errors[0]


def test_password_validation_valid():
    """Senha válida não deve retornar erros."""
    errors = validate_password_strength("senhasegura123")
    assert errors == []


def test_password_validation_exactly_min():
    """Senha com exatamente 10 caracteres deve ser válida."""
    errors = validate_password_strength("1234567890")
    assert errors == []
