"""Endpoints administrativos de políticos."""

import math
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import (
    get_audit_service,
    get_client_ip,
    get_current_verified_user,
    require_permission,
)
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.politician import (
    AliasCreateRequest,
    AliasResponse,
    ChangeHistoryResponse,
    MandateCreateRequest,
    MembershipCreateRequest,
    PoliticianCreateRequest,
    PoliticianDetailResponse,
    PoliticianListResponse,
    PoliticianListItem,
    PoliticianUpdateRequest,
    PartyResponse,
    SocialLinkCreateRequest,
)
from app.services.audit import AuditService
from app.services.politician import PoliticianService

router = APIRouter(prefix="/admin/politicians", tags=["Admin Políticos"])


def _get_service(
    db: AsyncSession = Depends(get_db),
    audit: AuditService = Depends(get_audit_service),
) -> PoliticianService:
    return PoliticianService(db, audit)


@router.post("", status_code=201)
async def create_politician(
    data: PoliticianCreateRequest,
    user: User = Depends(require_permission("politicians.create")),
    service: PoliticianService = Depends(_get_service),
    ip: str | None = Depends(get_client_ip),
):
    """Cria novo político (não publicado por padrão)."""
    politician = await service.create(
        full_name=data.full_name,
        created_by=user.email,
        ballot_name=data.ballot_name,
        biography=data.biography,
        birth_date=data.birth_date,
        birth_place=data.birth_place,
        gender=data.gender,
        marital_status=data.marital_status,
        education=data.education,
        occupation=data.occupation,
        photo_url=data.photo_url,
        state_code=data.state_code,
        city_name=data.city_name,
        website_url=data.website_url,
        current_party_id=data.current_party_id,
        current_position_id=data.current_position_id,
        source_url=data.source_url,
        ip=ip,
    )
    return {"id": politician.id, "slug": politician.slug, "message": "Político criado."}


@router.get("")
async def list_politicians_admin(
    q: str | None = Query(None),
    state: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(require_permission("politicians.read")),
    service: PoliticianService = Depends(_get_service),
):
    """Lista todos os políticos (incluindo não publicados)."""
    politicians, total = await service.search(
        q=q, state=state, page=page, limit=limit, include_unpublished=True,
    )
    pages = math.ceil(total / limit) if total > 0 else 0
    items = [
        {
            "id": p.id, "full_name": p.full_name, "slug": p.slug,
            "is_public": p.is_public, "state_code": p.state_code,
            "current_status": p.current_status, "created_at": p.created_at.isoformat(),
        }
        for p in politicians
    ]
    return {"items": items, "total": total, "page": page, "limit": limit, "pages": pages}


@router.get("/{politician_id}")
async def get_politician_admin(
    politician_id: uuid.UUID,
    user: User = Depends(require_permission("politicians.read")),
    service: PoliticianService = Depends(_get_service),
):
    """Retorna político completo (admin)."""
    p = await service.get_by_id(politician_id)
    if not p:
        raise NotFoundError(detail="Político não encontrado.")
    return {
        "id": p.id, "full_name": p.full_name, "ballot_name": p.ballot_name,
        "slug": p.slug, "biography": p.biography, "birth_date": str(p.birth_date) if p.birth_date else None,
        "state_code": p.state_code, "city_name": p.city_name,
        "current_status": p.current_status, "is_public": p.is_public,
        "is_verified": p.is_verified, "photo_url": p.photo_url,
        "website_url": p.website_url, "version": p.version,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }


@router.patch("/{politician_id}")
async def update_politician(
    politician_id: uuid.UUID,
    data: PoliticianUpdateRequest,
    user: User = Depends(require_permission("politicians.update")),
    service: PoliticianService = Depends(_get_service),
    ip: str | None = Depends(get_client_ip),
):
    """Atualiza político existente."""
    fields = data.model_dump(exclude_none=True)
    politician = await service.update(
        politician_id, updated_by=user.email, ip=ip, **fields
    )
    return {"id": politician.id, "message": "Político atualizado."}


@router.delete("/{politician_id}", response_model=MessageResponse)
async def delete_politician(
    politician_id: uuid.UUID,
    user: User = Depends(require_permission("politicians.delete")),
    service: PoliticianService = Depends(_get_service),
    ip: str | None = Depends(get_client_ip),
):
    """Soft delete de político."""
    await service.soft_delete(politician_id, ip)
    return MessageResponse(message="Político removido.")


@router.post("/{politician_id}/publish", response_model=MessageResponse)
async def publish_politician(
    politician_id: uuid.UUID,
    user: User = Depends(require_permission("politicians.update")),
    service: PoliticianService = Depends(_get_service),
    ip: str | None = Depends(get_client_ip),
):
    """Publica político (torna visível publicamente)."""
    await service.publish(politician_id, user.email, ip)
    return MessageResponse(message="Político publicado.")


@router.post("/{politician_id}/unpublish", response_model=MessageResponse)
async def unpublish_politician(
    politician_id: uuid.UUID,
    user: User = Depends(require_permission("politicians.update")),
    service: PoliticianService = Depends(_get_service),
    ip: str | None = Depends(get_client_ip),
):
    """Despublica político."""
    await service.unpublish(politician_id, ip)
    return MessageResponse(message="Político despublicado.")


@router.get("/{politician_id}/history")
async def get_politician_history(
    politician_id: uuid.UUID,
    user: User = Depends(require_permission("politicians.read")),
    service: PoliticianService = Depends(_get_service),
):
    """Retorna histórico de alterações."""
    history = await service.get_history(politician_id)
    return [
        ChangeHistoryResponse(
            id=h.id, field_name=h.field_name,
            old_value=h.old_value, new_value=h.new_value,
            change_reason=h.change_reason, changed_by=h.changed_by,
            created_at=h.created_at,
        )
        for h in history
    ]


# --- Aliases ---

@router.post("/{politician_id}/aliases")
async def add_alias(
    politician_id: uuid.UUID,
    data: AliasCreateRequest,
    user: User = Depends(require_permission("politicians.update")),
    service: PoliticianService = Depends(_get_service),
):
    """Adiciona alias ao político."""
    alias = await service.add_alias(
        politician_id, data.alias, data.alias_type, data.source_id
    )
    return {"id": alias.id, "message": "Alias adicionado."}


# --- Memberships ---

@router.post("/{politician_id}/memberships")
async def add_membership(
    politician_id: uuid.UUID,
    data: MembershipCreateRequest,
    user: User = Depends(require_permission("politicians.update")),
    service: PoliticianService = Depends(_get_service),
):
    """Adiciona filiação partidária."""
    membership = await service.add_membership(
        politician_id, data.party_id, data.started_at, data.ended_at,
        data.state_code, data.is_current, data.source_url,
    )
    return {"id": membership.id, "message": "Filiação registrada."}


# --- Mandates ---

@router.post("/{politician_id}/mandates")
async def add_mandate(
    politician_id: uuid.UUID,
    data: MandateCreateRequest,
    user: User = Depends(require_permission("politicians.update")),
    service: PoliticianService = Depends(_get_service),
):
    """Adiciona mandato."""
    mandate = await service.add_mandate(
        politician_id, data.position_id, data.party_id,
        data.state_code, data.city_name, data.started_at, data.ended_at,
        data.status, data.source_url,
    )
    return {"id": mandate.id, "message": "Mandato registrado."}


# --- Social Links ---

@router.post("/{politician_id}/social-links")
async def add_social_link(
    politician_id: uuid.UUID,
    data: SocialLinkCreateRequest,
    user: User = Depends(require_permission("politicians.update")),
    service: PoliticianService = Depends(_get_service),
):
    """Adiciona link de rede social."""
    link = await service.add_social_link(
        politician_id, data.platform, data.url, data.username, data.is_official,
    )
    return {"id": link.id, "message": "Link adicionado."}
