"""Endpoints de autenticação em dois fatores (MFA/TOTP)."""

import uuid
from datetime import UTC, datetime, timedelta

import pyotp
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from app.api.v1.dependencies import (
    get_auth_service,
    get_client_ip,
    get_current_user,
)
from app.core.config import get_settings
from app.core.exceptions import ForbiddenError, ValidationError
from app.core.rate_limiter import RATE_LIMITS, build_rate_key, rate_limiter
from app.core.redis import RedisStore
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_secure_token,
    hash_token,
    verify_password,
)
from app.models.user import Session, User
from app.schemas.auth import (
    MfaConfirmRequest,
    MfaSetupResponse,
    MfaVerifyRequest,
    MessageResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth/mfa", tags=["MFA"])
settings = get_settings()

MFA_SETUP_TTL_SECONDS = 600  # 10 minutes
MFA_SETUP_MAX_ATTEMPTS = 5


def _mfa_setup_key(user_id: uuid.UUID, challenge_id: str) -> str:
    """Chave Redis para MFA setup pendente."""
    return f"mfa_setup:{user_id}:{challenge_id}"


class MfaDisableRequest(BaseModel):
    password: str
    code: str


class MfaRegenerateRequest(BaseModel):
    password: str
    code: str


@router.post("/setup", response_model=MfaSetupResponse)
async def mfa_setup(
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Inicia configuração de MFA.
    Retorna secret, QR code URI e códigos de recuperação.
    Dados temporários armazenados no Redis (TTL 10 min).
    """
    secret, uri, recovery_codes = await auth_service.setup_mfa(user.id)

    # Store in Redis with challenge ID
    challenge_id = generate_secure_token(16)
    await RedisStore.set_json(
        _mfa_setup_key(user.id, challenge_id),
        {
            "recovery_codes": recovery_codes,
            "created_at": datetime.now(UTC).isoformat(),
            "attempts": 0,
        },
        MFA_SETUP_TTL_SECONDS,
    )

    return MfaSetupResponse(
        secret=secret,
        qr_code_uri=uri,
        recovery_codes=recovery_codes,
        challenge_id=challenge_id,
    )


class MfaConfirmWithChallenge(BaseModel):
    code: str
    challenge_id: str


@router.post("/confirm", response_model=MessageResponse)
async def mfa_confirm(
    data: MfaConfirmWithChallenge,
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
):
    """Confirma ativação do MFA com código TOTP válido."""
    redis_key = _mfa_setup_key(user.id, data.challenge_id)
    setup_data = await RedisStore.get_json(redis_key)

    if not setup_data:
        raise ValidationError(detail="Configuração expirada. Inicie novamente via /mfa/setup.")

    # Check attempt limit
    attempts = setup_data.get("attempts", 0)
    if attempts >= MFA_SETUP_MAX_ATTEMPTS:
        await RedisStore.delete(redis_key)
        raise ValidationError(detail="Limite de tentativas excedido. Inicie novamente.")

    recovery_codes = setup_data["recovery_codes"]
    success = await auth_service.confirm_mfa(user.id, data.code, recovery_codes, ip)

    if not success:
        # Increment attempts
        setup_data["attempts"] = attempts + 1
        await RedisStore.set_json(redis_key, setup_data, MFA_SETUP_TTL_SECONDS)
        raise ValidationError(detail="Código TOTP inválido.")

    # Clean up Redis
    await RedisStore.delete(redis_key)
    return MessageResponse(message="MFA ativado com sucesso.")


@router.post("/verify", response_model=MessageResponse)
async def mfa_verify(
    data: MfaVerifyRequest,
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    response: Response = None,
    ip: str | None = Depends(get_client_ip),
):
    """
    Verifica código MFA durante login (quando mfa_required=True).
    Completa a autenticação e define cookies completos.
    """
    key = build_rate_key("mfa_verify", ip or "unknown", str(user.id))
    limit = RATE_LIMITS["mfa_verify"]
    if await rate_limiter.is_rate_limited(key, limit["max_attempts"], limit["window_seconds"]):
        raise ValidationError(detail="Limite de tentativas excedido.")
    await rate_limiter.increment(key, limit["window_seconds"])

    if not user.mfa_secret:
        raise ValidationError(detail="MFA não configurado.")

    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(data.code, valid_window=1):
        # Try recovery code
        if not await auth_service._use_recovery_code(user.id, data.code):
            raise ValidationError(detail="Código inválido.")

    # Issue full tokens
    roles = [ur.role.name for ur in user.roles]
    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"roles": roles, "mfa_verified": True},
    )
    refresh_raw, family = create_refresh_token(subject=str(user.id))

    session_model = Session(
        user_id=user.id,
        refresh_token_hash=hash_token(refresh_raw),
        token_family=family,
        ip_address=ip,
        is_active=True,
        expires_at=datetime.now(UTC) + timedelta(days=settings.jwt_refresh_expires_days),
        last_used_at=datetime.now(UTC),
    )
    auth_service.db.add(session_model)
    await auth_service.db.flush()

    # Set cookies
    is_prod = settings.app_env == "production"
    if response:
        response.set_cookie(
            key="access_token", value=access_token,
            httponly=True, secure=is_prod, samesite="lax",
            max_age=settings.jwt_access_expires_minutes * 60, path="/",
        )
        response.set_cookie(
            key="refresh_token", value=refresh_raw,
            httponly=True, secure=is_prod, samesite="lax",
            max_age=settings.jwt_refresh_expires_days * 86400, path="/api/v1/auth",
        )

    await rate_limiter.reset(key)
    return MessageResponse(message="MFA verificado com sucesso.")


@router.post("/disable", response_model=MessageResponse)
async def mfa_disable(
    data: MfaDisableRequest,
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
):
    """Desativa MFA. Requer senha e código TOTP."""
    await auth_service.disable_mfa(
        user_id=user.id,
        password=data.password,
        code=data.code,
        ip=ip,
    )
    return MessageResponse(message="MFA desativado com sucesso.")


@router.post("/recovery-codes/regenerate")
async def regenerate_recovery_codes(
    data: MfaRegenerateRequest,
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
):
    """Regenera códigos de recuperação. Requer senha e código MFA."""
    codes = await auth_service.regenerate_recovery_codes(
        user_id=user.id,
        password=data.password,
        code=data.code,
        ip=ip,
    )
    return {"recovery_codes": codes}
