"""Dependencies de autenticação e autorização para FastAPI."""

import uuid
from collections.abc import Callable
from functools import wraps

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.models.user import User
from app.services.audit import AuditService
from app.services.auth import AuthService


def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    """Dependency para AuditService."""
    return AuditService(db)


def get_auth_service(
    db: AsyncSession = Depends(get_db),
    audit: AuditService = Depends(get_audit_service),
) -> AuthService:
    """Dependency para AuthService."""
    return AuthService(db, audit)


def get_client_ip(request: Request) -> str | None:
    """Extrai IP do cliente."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def get_user_agent(request: Request) -> str | None:
    """Extrai user agent."""
    return request.headers.get("User-Agent")


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extrai e valida o usuário autenticado a partir do cookie ou header.
    """
    # Try cookie first, then Authorization header
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise UnauthorizedError(detail="Não autenticado.")

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedError(detail="Token inválido.")

    # Check MFA verification
    if payload.get("mfa_verified") is False:
        raise ForbiddenError(detail="Verificação MFA necessária.")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError(detail="Token inválido.")

    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise UnauthorizedError(detail="Token inválido.")

    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedError(detail="Conta inativa.")

    return user


async def get_current_verified_user(
    user: User = Depends(get_current_user),
) -> User:
    """Requer que o usuário tenha e-mail verificado."""
    if not user.is_verified:
        raise ForbiddenError(detail="E-mail não verificado.")
    return user


def require_permission(permission_name: str) -> Callable:
    """Cria dependency que exige permissão específica."""

    async def check_permission(
        user: User = Depends(get_current_verified_user),
    ) -> User:
        user_permissions: set[str] = set()
        for user_role in user.roles:
            role = user_role.role
            for rp in role.permissions:
                user_permissions.add(rp.permission.name)

        if permission_name not in user_permissions:
            raise ForbiddenError(detail="Permissão insuficiente.")
        return user

    return check_permission


def require_role(role_name: str) -> Callable:
    """Cria dependency que exige role específica."""

    async def check_role(
        user: User = Depends(get_current_verified_user),
    ) -> User:
        user_roles = {ur.role.name for ur in user.roles}
        if role_name not in user_roles:
            raise ForbiddenError(detail="Acesso restrito.")
        return user

    return check_role


async def require_mfa(user: User = Depends(get_current_user)) -> User:
    """Requer que o usuário tenha MFA ativado."""
    if not user.mfa_enabled:
        raise ForbiddenError(detail="MFA obrigatório para esta ação.")
    return user
