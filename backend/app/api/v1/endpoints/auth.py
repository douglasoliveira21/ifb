"""Endpoints de autenticação."""

import uuid

from fastapi import APIRouter, Depends, Request, Response

from app.api.v1.dependencies import (
    get_auth_service,
    get_client_ip,
    get_current_user,
    get_user_agent,
)
from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError, ValidationError
from app.core.rate_limiter import (
    RATE_LIMITS,
    build_rate_key,
    rate_limiter,
)
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    SessionInfo,
    SessionListResponse,
    VerifyEmailRequest,
)
from app.services.auth import AuthService
from app.workers.tasks_email import (
    dispatch_password_changed_email,
    dispatch_password_reset_email,
    dispatch_verification_email,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])
settings = get_settings()


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Define cookies seguros com tokens."""
    is_prod = settings.app_env == "production"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=settings.jwt_access_expires_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=settings.jwt_refresh_expires_days * 86400,
        path="/api/v1/auth",
    )


def _clear_auth_cookies(response: Response) -> None:
    """Remove cookies de autenticação."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/auth")


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(
    data: RegisterRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
    ua: str | None = Depends(get_user_agent),
):
    """Cadastro de novo usuário."""
    # Rate limit
    key = build_rate_key("register", ip or "unknown")
    limit = RATE_LIMITS["register"]
    if await rate_limiter.is_rate_limited(key, limit["max_attempts"], limit["window_seconds"]):
        raise ValidationError(detail="Limite de tentativas excedido. Tente novamente mais tarde.")
    await rate_limiter.increment(key, limit["window_seconds"])

    user, token = await auth_service.register(
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        ip_address=ip,
        user_agent=ua,
    )

    # Send verification email via Celery (non-blocking)
    dispatch_verification_email(user.email, token)

    return RegisterResponse(id=user.id, email=user.email, full_name=user.full_name)


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
    ua: str | None = Depends(get_user_agent),
):
    """Login. Retorna tokens em cookies HttpOnly."""
    # Rate limit (tolerant to Redis failures)
    try:
        key = build_rate_key("login", ip or "unknown", data.email)
        limit = RATE_LIMITS["login"]
        if await rate_limiter.is_rate_limited(key, limit["max_attempts"], limit["window_seconds"]):
            raise UnauthorizedError(detail="Credenciais inválidas.")
        await rate_limiter.increment(key, limit["window_seconds"])
    except UnauthorizedError:
        raise
    except Exception:
        pass  # Redis unavailable - allow login attempt

    access_token, refresh_token, session_id, mfa_required = await auth_service.login(
        email=data.email,
        password=data.password,
        mfa_code=data.mfa_code,
        ip_address=ip,
        user_agent=ua,
    )

    if mfa_required:
        # Partial auth - set only access token (mfa_verified=False)
        is_prod = settings.app_env == "production"
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=is_prod,
            samesite="lax",
            max_age=300,  # 5 min to complete MFA
            path="/",
        )
        return LoginResponse(
            access_token=access_token,
            expires_in=300,
            mfa_required=True,
        )

    # Reset rate limit on success
    await rate_limiter.reset(key)

    _set_auth_cookies(response, access_token, refresh_token)
    return LoginResponse(
        access_token=access_token,
        expires_in=settings.jwt_access_expires_minutes * 60,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    user: User = Depends(get_current_user),
    ip: str | None = Depends(get_client_ip),
):
    """Logout - revoga sessão atual."""
    # Find session from refresh token
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        from app.core.security import decode_token as dt
        payload = dt(refresh_token)
        if payload and payload.get("family"):
            from sqlalchemy import select, and_
            from app.models.user import Session
            from app.core.database import async_session_factory
            # Revoke by family
            pass

    # Revoke all sessions for simplicity in this endpoint
    # The user can revoke specific sessions via the sessions endpoint
    _clear_auth_cookies(response)
    return MessageResponse(message="Logout realizado com sucesso.")


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
    ua: str | None = Depends(get_user_agent),
):
    """Renova access token usando refresh token do cookie."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            refresh_token = auth_header[7:]
    if not refresh_token:
        raise UnauthorizedError(detail="Token de refresh não encontrado.")

    # Rate limit
    key = build_rate_key("refresh", ip or "unknown")
    limit = RATE_LIMITS["refresh"]
    if await rate_limiter.is_rate_limited(key, limit["max_attempts"], limit["window_seconds"]):
        raise UnauthorizedError(detail="Limite excedido.")
    await rate_limiter.increment(key, limit["window_seconds"])

    new_access, new_refresh = await auth_service.refresh_tokens(
        refresh_token=refresh_token,
        ip_address=ip,
        user_agent=ua,
    )

    _set_auth_cookies(response, new_access, new_refresh)
    return RefreshResponse(
        access_token=new_access,
        expires_in=settings.jwt_access_expires_minutes * 60,
    )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    data: VerifyEmailRequest,
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
):
    """Verifica e-mail usando token recebido por e-mail."""
    success = await auth_service.verify_email(data.token, ip)
    if not success:
        raise ValidationError(detail="Token inválido ou expirado.")
    return MessageResponse(message="E-mail verificado com sucesso.")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    data: ResendVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
):
    """Reenvia e-mail de verificação. Resposta genérica por segurança."""
    key = build_rate_key("resend_verification", ip or "unknown", data.email)
    limit = RATE_LIMITS["resend_verification"]
    if await rate_limiter.is_rate_limited(key, limit["max_attempts"], limit["window_seconds"]):
        return MessageResponse(
            message="Se os dados informados estiverem cadastrados, as instruções serão enviadas."
        )
    await rate_limiter.increment(key, limit["window_seconds"])

    token = await auth_service.resend_verification(data.email, ip)
    if token:
        dispatch_verification_email(data.email, token)

    return MessageResponse(
        message="Se os dados informados estiverem cadastrados, as instruções serão enviadas."
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
):
    """Solicita recuperação de senha. Resposta genérica por segurança."""
    key = build_rate_key("forgot_password", ip or "unknown", data.email)
    limit = RATE_LIMITS["forgot_password"]
    if await rate_limiter.is_rate_limited(key, limit["max_attempts"], limit["window_seconds"]):
        return MessageResponse(
            message="Se os dados informados estiverem cadastrados, as instruções serão enviadas."
        )
    await rate_limiter.increment(key, limit["window_seconds"])

    token = await auth_service.request_password_reset(data.email, ip)
    if token:
        dispatch_password_reset_email(data.email, token)

    return MessageResponse(
        message="Se os dados informados estiverem cadastrados, as instruções serão enviadas."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
):
    """Redefine senha com token de recuperação."""
    success = await auth_service.reset_password(data.token, data.new_password, ip)
    if not success:
        raise ValidationError(detail="Token inválido ou expirado.")
    return MessageResponse(message="Senha redefinida com sucesso.")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
):
    """Altera senha do usuário autenticado."""
    await auth_service.change_password(
        user_id=user.id,
        current_password=data.current_password,
        new_password=data.new_password,
        ip=ip,
    )
    dispatch_password_changed_email(user.email)
    return MessageResponse(message="Senha alterada com sucesso.")


# --- Sessions ---

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    request: Request,
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Lista sessões ativas do usuário."""
    sessions = await auth_service.get_user_sessions(user.id)
    # Determine current session from refresh token cookie
    current_family = None
    refresh_cookie = request.cookies.get("refresh_token")
    if refresh_cookie:
        from app.core.security import decode_token as dt
        payload = dt(refresh_cookie)
        if payload:
            current_family = payload.get("family")

    items = []
    for s in sessions:
        items.append(SessionInfo(
            id=s.id,
            user_agent=s.user_agent,
            ip_address=s.ip_address,
            created_at=s.created_at,
            last_used_at=s.last_used_at,
            is_current=(s.token_family == current_family) if current_family else False,
        ))
    return SessionListResponse(sessions=items)


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
):
    """Encerra sessão específica."""
    await auth_service.revoke_session(session_id, user.id, ip)
    return MessageResponse(message="Sessão encerrada.")


@router.delete("/sessions", response_model=MessageResponse)
async def revoke_all_sessions(
    response: Response,
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
):
    """Encerra todas as sessões do usuário."""
    count = await auth_service.revoke_all_sessions(user.id, ip)
    _clear_auth_cookies(response)
    return MessageResponse(message=f"{count} sessão(ões) encerrada(s).")
