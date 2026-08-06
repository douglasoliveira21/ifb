"""Endpoints administrativos de RBAC (roles e permissões)."""

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import (
    get_audit_service,
    get_client_ip,
    get_current_verified_user,
    require_role,
)
from app.core.database import get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import Permission, Role, User, UserRole
from app.schemas.auth import MessageResponse
from app.services.audit import AuditEvents, AuditService

router = APIRouter(prefix="/admin", tags=["Administração RBAC"])


# --- Schemas específicos ---

class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    is_active: bool


class RoleCreateRequest(BaseModel):
    name: str
    display_name: str
    description: str | None = None


class RoleUpdateRequest(BaseModel):
    display_name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class PermissionResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    resource: str
    action: str


class AssignRoleRequest(BaseModel):
    role_id: uuid.UUID


# --- Roles ---

@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin")),
):
    """Lista todas as roles."""
    result = await db.execute(select(Role).order_by(Role.name))
    roles = result.scalars().all()
    return [
        RoleResponse(
            id=r.id, name=r.name, display_name=r.display_name,
            description=r.description, is_active=r.is_active,
        )
        for r in roles
    ]


@router.post("/roles", response_model=RoleResponse, status_code=201)
async def create_role(
    data: RoleCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("superadmin")),
    audit: AuditService = Depends(get_audit_service),
    ip: str | None = Depends(get_client_ip),
):
    """Cria nova role (somente superadmin)."""
    existing = await db.execute(select(Role).where(Role.name == data.name))
    if existing.scalar_one_or_none():
        raise ConflictError(detail="Role já existe.")

    role = Role(
        name=data.name,
        display_name=data.display_name,
        description=data.description,
    )
    db.add(role)
    await db.flush()

    await audit.log(
        AuditEvents.ROLE_CREATED, "role",
        user_id=admin.id, resource_id=str(role.id),
        ip_address=ip, new_value={"name": role.name},
    )
    return RoleResponse(
        id=role.id, name=role.name, display_name=role.display_name,
        description=role.description, is_active=role.is_active,
    )


@router.patch("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: uuid.UUID,
    data: RoleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("superadmin")),
    audit: AuditService = Depends(get_audit_service),
    ip: str | None = Depends(get_client_ip),
):
    """Atualiza role existente (somente superadmin)."""
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise NotFoundError(detail="Role não encontrada.")

    old_values = {"display_name": role.display_name, "is_active": role.is_active}
    if data.display_name is not None:
        role.display_name = data.display_name
    if data.description is not None:
        role.description = data.description
    if data.is_active is not None:
        role.is_active = data.is_active
    await db.flush()

    await audit.log(
        AuditEvents.ROLE_UPDATED, "role",
        user_id=admin.id, resource_id=str(role.id),
        old_value=old_values, ip_address=ip,
    )
    return RoleResponse(
        id=role.id, name=role.name, display_name=role.display_name,
        description=role.description, is_active=role.is_active,
    )


@router.delete("/roles/{role_id}", response_model=MessageResponse)
async def delete_role(
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("superadmin")),
    audit: AuditService = Depends(get_audit_service),
    ip: str | None = Depends(get_client_ip),
):
    """Remove role (soft - desativa)."""
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise NotFoundError(detail="Role não encontrada.")

    # Protect system roles
    if role.name in ("superadmin", "admin", "user"):
        raise ConflictError(detail="Não é possível remover roles do sistema.")

    role.is_active = False
    await db.flush()
    await audit.log(
        AuditEvents.ROLE_DELETED, "role",
        user_id=admin.id, resource_id=str(role.id), ip_address=ip,
    )
    return MessageResponse(message="Role desativada.")


# --- Permissions ---

@router.get("/permissions", response_model=list[PermissionResponse])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin")),
):
    """Lista todas as permissões."""
    result = await db.execute(select(Permission).order_by(Permission.name))
    perms = result.scalars().all()
    return [
        PermissionResponse(
            id=p.id, name=p.name, description=p.description,
            resource=p.resource, action=p.action,
        )
        for p in perms
    ]


# --- User Roles ---

@router.post("/users/{user_id}/roles", response_model=MessageResponse)
async def assign_role(
    user_id: uuid.UUID,
    data: AssignRoleRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
    audit: AuditService = Depends(get_audit_service),
    ip: str | None = Depends(get_client_ip),
):
    """Atribui role a um usuário."""
    # Verify target user exists
    from app.models.user import User as UserModel
    target = await db.execute(select(UserModel).where(UserModel.id == user_id))
    if not target.scalar_one_or_none():
        raise NotFoundError(detail="Usuário não encontrado.")

    # Verify role exists
    role = await db.execute(select(Role).where(Role.id == data.role_id))
    role_obj = role.scalar_one_or_none()
    if not role_obj:
        raise NotFoundError(detail="Role não encontrada.")

    # Check not already assigned
    existing = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == data.role_id
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(detail="Usuário já possui esta role.")

    user_role = UserRole(
        user_id=user_id,
        role_id=data.role_id,
        assigned_by=admin.email,
    )
    db.add(user_role)
    await db.flush()

    await audit.log(
        AuditEvents.ROLE_ASSIGNED, "user_role",
        user_id=admin.id, resource_id=str(user_id),
        details={"role": role_obj.name}, ip_address=ip,
    )
    return MessageResponse(message=f"Role '{role_obj.name}' atribuída.")


@router.delete("/users/{user_id}/roles/{role_id}", response_model=MessageResponse)
async def remove_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
    audit: AuditService = Depends(get_audit_service),
    ip: str | None = Depends(get_client_ip),
):
    """Remove role de um usuário."""
    result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )
    )
    user_role = result.scalar_one_or_none()
    if not user_role:
        raise NotFoundError(detail="Associação não encontrada.")

    await db.delete(user_role)
    await db.flush()

    await audit.log(
        AuditEvents.ROLE_REMOVED, "user_role",
        user_id=admin.id, resource_id=str(user_id),
        details={"role_id": str(role_id)}, ip_address=ip,
    )
    return MessageResponse(message="Role removida do usuário.")
