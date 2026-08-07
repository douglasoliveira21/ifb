"""Endpoint público de partidos políticos."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.politician import Politician, PoliticalParty, PoliticalPosition

router = APIRouter(prefix="/parties", tags=["Partidos"])


@router.get("")
async def list_parties(
    status: str = Query("active", description="Filtro por status"),
    db: AsyncSession = Depends(get_db),
):
    """Lista partidos ativos com contagem de parlamentares."""
    # Get all active parties
    parties_result = await db.execute(
        select(PoliticalParty).where(PoliticalParty.status == status).order_by(PoliticalParty.acronym)
    )
    parties = parties_result.scalars().all()

    items = []
    for party in parties:
        # Count total politicians
        total_count = (
            await db.execute(
                select(func.count(Politician.id)).where(
                    Politician.current_party_id == party.id,
                    Politician.is_public == True,
                    Politician.deleted_at == None,
                )
            )
        ).scalar_one()

        if total_count == 0:
            continue

        # Count by position
        dep_pos = await db.execute(
            select(PoliticalPosition.id).where(PoliticalPosition.name == "Deputado Federal")
        )
        dep_pos_id = dep_pos.scalar_one_or_none()

        sen_pos = await db.execute(
            select(PoliticalPosition.id).where(PoliticalPosition.name == "Senador")
        )
        sen_pos_id = sen_pos.scalar_one_or_none()

        deputies_count = 0
        senators_count = 0

        if dep_pos_id:
            deputies_count = (
                await db.execute(
                    select(func.count(Politician.id)).where(
                        Politician.current_party_id == party.id,
                        Politician.current_position_id == dep_pos_id,
                        Politician.is_public == True,
                        Politician.deleted_at == None,
                    )
                )
            ).scalar_one()

        if sen_pos_id:
            senators_count = (
                await db.execute(
                    select(func.count(Politician.id)).where(
                        Politician.current_party_id == party.id,
                        Politician.current_position_id == sen_pos_id,
                        Politician.is_public == True,
                        Politician.deleted_at == None,
                    )
                )
            ).scalar_one()

        items.append({
            "id": str(party.id),
            "name": party.name,
            "acronym": party.acronym,
            "electoral_number": party.electoral_number,
            "logo_url": party.logo_url,
            "official_url": party.official_url,
            "status": party.status,
            "total_politicians": total_count,
            "deputies": deputies_count,
            "senators": senators_count,
        })

    return {"items": items, "total": len(items)}


@router.get("/{acronym}")
async def get_party_detail(
    acronym: str,
    db: AsyncSession = Depends(get_db),
):
    """Retorna detalhes de um partido com lista de parlamentares."""
    result = await db.execute(
        select(PoliticalParty).where(PoliticalParty.acronym == acronym.upper())
    )
    party = result.scalar_one_or_none()
    if not party:
        raise NotFoundError(detail="Partido não encontrado.")

    # Get politicians of this party
    pols_result = await db.execute(
        select(Politician).where(
            Politician.current_party_id == party.id,
            Politician.is_public == True,
            Politician.deleted_at == None,
        ).order_by(Politician.full_name).limit(100)
    )
    politicians = pols_result.scalars().all()

    # Get position names
    dep_pos = await db.execute(
        select(PoliticalPosition.id).where(PoliticalPosition.name == "Deputado Federal")
    )
    dep_pos_id = dep_pos.scalar_one_or_none()

    sen_pos = await db.execute(
        select(PoliticalPosition.id).where(PoliticalPosition.name == "Senador")
    )
    sen_pos_id = sen_pos.scalar_one_or_none()

    members = []
    for p in politicians:
        position_name = None
        if p.current_position_id == dep_pos_id:
            position_name = "Deputado Federal"
        elif p.current_position_id == sen_pos_id:
            position_name = "Senador"

        members.append({
            "id": str(p.id),
            "full_name": p.full_name,
            "ballot_name": p.ballot_name,
            "slug": p.slug,
            "photo_url": p.photo_url,
            "state_code": p.state_code,
            "position": position_name,
        })

    return {
        "id": str(party.id),
        "name": party.name,
        "acronym": party.acronym,
        "electoral_number": party.electoral_number,
        "logo_url": party.logo_url,
        "official_url": party.official_url,
        "status": party.status,
        "total_politicians": len(members),
        "deputies": sum(1 for m in members if m["position"] == "Deputado Federal"),
        "senators": sum(1 for m in members if m["position"] == "Senador"),
        "members": members,
    }
