"""Módulo de segurança: hashing, JWT, tokens e MFA."""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()
ph = PasswordHasher()


# --- Password Hashing (Argon2id) ---


def hash_password(password: str) -> str:
    """Gera hash Argon2id da senha."""
    return ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verifica senha contra hash Argon2id."""
    try:
        return ph.verify(hashed, password)
    except VerifyMismatchError:
        return False


# --- JWT Tokens ---


def create_access_token(
    subject: str,
    extra_claims: dict | None = None,
) -> str:
    """Cria JWT de acesso com expiração curta (15min padrão)."""
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.jwt_access_expires_minutes)
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, family: str | None = None) -> tuple[str, str]:
    """
    Cria refresh token.
    Retorna (token_raw, token_family).
    O token_raw deve ser enviado ao cliente; o hash deve ser armazenado.
    """
    token_family = family or str(uuid.uuid4())
    now = datetime.now(UTC)
    expire = now + timedelta(days=settings.jwt_refresh_expires_days)
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "type": "refresh",
        "family": token_family,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, token_family


def decode_token(token: str) -> dict | None:
    """Decodifica e valida um JWT. Retorna None se inválido ou expirado."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


# --- Secure Token Generation ---


def generate_secure_token(nbytes: int = 32) -> str:
    """Gera token criptograficamente seguro (URL-safe)."""
    return secrets.token_urlsafe(nbytes)


def hash_token(token: str) -> str:
    """Cria SHA-256 hash de um token para armazenamento."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """Verifica se um token corresponde ao hash armazenado."""
    return secrets.compare_digest(hash_token(token), token_hash)


# --- Password Validation ---


MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128


def validate_password_strength(password: str) -> list[str]:
    """
    Valida força da senha. Retorna lista de erros (vazia = válida).
    Sem regras artificiais excessivas, apenas comprimento mínimo.
    """
    errors: list[str] = []
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"A senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres.")
    if len(password) > MAX_PASSWORD_LENGTH:
        errors.append(f"A senha deve ter no máximo {MAX_PASSWORD_LENGTH} caracteres.")
    return errors
