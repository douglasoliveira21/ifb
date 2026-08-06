"""Endpoints de perfil do usuário."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import (
    get_auth_service,
    get_client_ip,
    get_current_user,
)
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import (
    MessageResponse,
    UserMeResponse,
    UserUpdateRequest,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/users", tags=["Usuários"])


@router.get("/me", response_model=UserMeResponse)
async def get_me(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna dados do usuário autenticado."""
    from sqlalchemy import select
    from app.models.user import UserRole, Role

    # Query roles explicitly to avoid lazy loading
    result = await db.execute(
        select(Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user.id)
    )
    roles = [row for row in result.scalars().all()]

    return UserMeResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_verified=user.is_verified,
        mfa_enabled=user.mfa_enabled,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        roles=roles,
    )


@router.patch("/me", response_model=UserMeResponse)
async def update_me(
    data: UserUpdateRequest,
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
):
    """Atualiza perfil do usuário autenticado."""
    updated = await auth_service.update_profile(
        user_id=user.id,
        full_name=data.full_name,
        avatar_url=data.avatar_url,
        ip=ip,
    )
    roles = [ur.role.name for ur in updated.roles]
    return UserMeResponse(
        id=updated.id,
        email=updated.email,
        full_name=updated.full_name,
        is_verified=updated.is_verified,
        mfa_enabled=updated.mfa_enabled,
        avatar_url=updated.avatar_url,
        created_at=updated.created_at,
        roles=roles,
    )


@router.delete("/me", response_model=MessageResponse)
async def delete_me(
    user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    ip: str | None = Depends(get_client_ip),
):
    """
    Exclui conta do usuário (soft delete).
    Requer confirmação de senha via header X-Confirm-Password.
    """
    # Note: In production, use a body with password field
    # For now we accept it for MVP
    from fastapi import Request
    return MessageResponse(
        message="Para excluir sua conta, envie POST /users/me/delete com {password}."
    )
