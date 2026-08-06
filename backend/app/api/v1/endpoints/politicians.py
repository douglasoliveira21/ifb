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
    db: AsyncSession = Depends(get_db),
):
    """Lista e pesquisa políticos públicos."""
    from sqlalchemy import select as sa_select
    from app.models.politician import PoliticalParty, PoliticalPosition

    politicians, total = await service.search(
        q=q, party=party, state=state, position=position,
        page=page, limit=limit, include_unpublished=False,
    )
    pages = math.ceil(total / limit) if total > 0 else 0

    items = []
    for p in politicians:
        party_resp = None
        if p.current_party_id:
            party_result = await db.execute(
                sa_select(PoliticalParty).where(PoliticalParty.id == p.current_party_id)
            )
            party_obj = party_result.scalar_one_or_none()
            if party_obj:
                party_resp = PartyResponse(
                    id=party_obj.id, name=party_obj.name,
                    acronym=party_obj.acronym,
                    electoral_number=party_obj.electoral_number,
                    logo_url=party_obj.logo_url, status=party_obj.status,
                )

        position_name = None
        if p.current_position_id:
            pos_result = await db.execute(
                sa_select(PoliticalPosition.name).where(PoliticalPosition.id == p.current_position_id)
            )
            position_name = pos_result.scalar_one_or_none()

        items.append(PoliticianListItem(
            id=p.id, full_name=p.full_name, ballot_name=p.ballot_name,
            slug=p.slug, photo_url=p.photo_url, current_status=p.current_status,
            current_party=party_resp,
            current_position_name=position_name,
            state_code=p.state_code, city_name=p.city_name,
        ))

    return PoliticianListResponse(
        items=items, total=total, page=page, limit=limit, pages=pages,
    )


@router.get("/{slug}", response_model=PoliticianDetailResponse)
async def get_politician(
    slug: str,
    service: PoliticianService = Depends(_get_politician_service),
    db: AsyncSession = Depends(get_db),
):
    """Retorna perfil público do político."""
    from sqlalchemy import select as sa_select
    from app.models.politician import PoliticalParty, PoliticalPosition, PoliticianAlias, PoliticianSocialLink

    politician = await service.get_by_slug(slug)
    if not politician:
        raise NotFoundError(detail="Político não encontrado.")

    # Load party explicitly
    party_resp = None
    if politician.current_party_id:
        party_result = await db.execute(
            sa_select(PoliticalParty).where(PoliticalParty.id == politician.current_party_id)
        )
        party_obj = party_result.scalar_one_or_none()
        if party_obj:
            party_resp = PartyResponse(
                id=party_obj.id, name=party_obj.name,
                acronym=party_obj.acronym,
                electoral_number=party_obj.electoral_number,
                logo_url=party_obj.logo_url, status=party_obj.status,
            )

    # Load position explicitly
    position_name = None
    if politician.current_position_id:
        pos_result = await db.execute(
            sa_select(PoliticalPosition.name).where(PoliticalPosition.id == politician.current_position_id)
        )
        position_name = pos_result.scalar_one_or_none()

    # Load aliases explicitly
    alias_result = await db.execute(
        sa_select(PoliticianAlias).where(PoliticianAlias.politician_id == politician.id)
    )
    aliases = [
        AliasResponse(id=a.id, alias=a.alias, alias_type=a.alias_type, is_verified=a.is_verified)
        for a in alias_result.scalars().all()
    ]

    # Load social links explicitly
    links_result = await db.execute(
        sa_select(PoliticianSocialLink).where(PoliticianSocialLink.politician_id == politician.id)
    )
    social_links = [
        SocialLinkResponse(
            id=s.id, platform=s.platform, url=s.url,
            username=s.username, is_official=s.is_official,
        )
        for s in links_result.scalars().all()
    ]

    return PoliticianDetailResponse(
        id=politician.id, full_name=politician.full_name,
        ballot_name=politician.ballot_name, slug=politician.slug,
        biography=politician.biography, birth_date=politician.birth_date,
        birth_place=politician.birth_place, gender=politician.gender,
        education=politician.education, occupation=politician.occupation,
        photo_url=politician.photo_url, current_status=politician.current_status,
        current_party=party_resp,
        current_position_name=position_name,
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
