"""Endpoints públicos de políticos."""

import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_audit_service
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.schemas.politician import (
    AliasResponse,
    MandateResponse,
    MembershipResponse,
    PartyResponse,
    PoliticianDetailResponse,
    PoliticianListItem,
    PoliticianListResponse,
    PoliticianSourceResponse,
    SocialLinkResponse,
)
from app.services.audit import AuditService
from app.services.politician import PoliticianService

router = APIRouter(prefix="/politicians", tags=["Políticos"])


def _get_politician_service(
    db: AsyncSession = Depends(get_db),
    audit: AuditService = Depends(get_audit_service),
) -> PoliticianService:
    return PoliticianService(db, audit)


@router.get("", response_model=PoliticianListResponse)
async def list_politicians(
    q: str | None = Query(None, description="Pesquisa por nome"),
    party: str | None = Query(None, description="Filtro por partido (sigla ou nome)"),
    state: str | None = Query(None, description="Filtro por UF", max_length=2),
    position: str | None = Query(None, description="Filtro por cargo"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: PoliticianService = Depends(_get_politician_service),
):
    """Lista e pesquisa políticos públicos."""
    politicians, total = await service.search(
        q=q, party=party, state=state, position=position,
        page=page, limit=limit, include_unpublished=False,
    )
    pages = math.ceil(total / limit) if total > 0 else 0

    items = []
    for p in politicians:
        party_resp = None
        if p.current_party:
            party_resp = PartyResponse(
                id=p.current_party.id, name=p.current_party.name,
                acronym=p.current_party.acronym,
                electoral_number=p.current_party.electoral_number,
                logo_url=p.current_party.logo_url, status=p.current_party.status,
            )
        items.append(PoliticianListItem(
            id=p.id, full_name=p.full_name, ballot_name=p.ballot_name,
            slug=p.slug, photo_url=p.photo_url, current_status=p.current_status,
            current_party=party_resp,
            current_position_name=p.current_position.name if p.current_position else None,
            state_code=p.state_code, city_name=p.city_name,
        ))

    return PoliticianListResponse(
        items=items, total=total, page=page, limit=limit, pages=pages,
    )


@router.get("/{slug}", response_model=PoliticianDetailResponse)
async def get_politician(
    slug: str,
    service: PoliticianService = Depends(_get_politician_service),
):
    """Retorna perfil público do político."""
    politician = await service.get_by_slug(slug)
    if not politician:
        raise NotFoundError(detail="Político não encontrado.")

    party_resp = None
    if politician.current_party:
        party_resp = PartyResponse(
            id=politician.current_party.id, name=politician.current_party.name,
            acronym=politician.current_party.acronym,
            electoral_number=politician.current_party.electoral_number,
            logo_url=politician.current_party.logo_url,
            status=politician.current_party.status,
        )

    aliases = [
        AliasResponse(id=a.id, alias=a.alias, alias_type=a.alias_type, is_verified=a.is_verified)
        for a in politician.aliases
    ]

    social_links = [
        SocialLinkResponse(
            id=s.id, platform=s.platform, url=s.url,
            username=s.username, is_official=s.is_official,
        )
        for s in (politician.social_links or [])
    ]

    return PoliticianDetailResponse(
        id=politician.id, full_name=politician.full_name,
        ballot_name=politician.ballot_name, slug=politician.slug,
        biography=politician.biography, birth_date=politician.birth_date,
        birth_place=politician.birth_place, gender=politician.gender,
        education=politician.education, occupation=politician.occupation,
        photo_url=politician.photo_url, current_status=politician.current_status,
        current_party=party_resp,
        current_position_name=politician.current_position.name if politician.current_position else None,
        state_code=politician.state_code, city_name=politician.city_name,
        website_url=politician.website_url, is_verified=politician.is_verified,
        data_quality_score=politician.data_quality_score,
        aliases=aliases, social_links=social_links,
        updated_at=politician.updated_at, source_url=politician.source_url,
    )


@router.get("/{slug}/sources", response_model=PoliticianSourceResponse)
async def get_politician_sources(
    slug: str,
    service: PoliticianService = Depends(_get_politician_service),
):
    """Retorna fontes de dados do político."""
    politician = await service.get_by_slug(slug)
    if not politician:
        raise NotFoundError(detail="Político não encontrado.")

    return PoliticianSourceResponse(
        source_id=politician.source_id,
        source_url=politician.source_url,
        collected_at=politician.collected_at,
        validated_at=politician.validated_at,
        validated_by=politician.validated_by,
    )
