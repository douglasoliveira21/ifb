"""API pública eleitoral — dados de candidaturas, bens, receitas, despesas e resultados."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, and_, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_audit_service
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.election import (
    CampaignAccountability,
    CampaignExpense,
    CampaignRevenue,
    CandidateAsset,
    Candidacy,
    Election,
    ElectionResult,
    GovernmentPlan,
)
from app.models.politician import Politician, PoliticalParty, PoliticalPosition

router = APIRouter(prefix="/politicians/{slug}", tags=["Dados Eleitorais"])


# --- Response schemas ---

class MetadataResponse(BaseModel):
    source: str = "Tribunal Superior Eleitoral"
    source_url: str = "https://dadosabertos.tse.jus.br"
    collected_at: datetime | None = None
    last_updated_at: datetime | None = None
    availability: str = "available"


class CandidacyItem(BaseModel):
    id: uuid.UUID
    election_year: int
    election_name: str
    position: str | None
    party_acronym: str | None
    ballot_name: str
    ballot_number: str | None
    state_code: str | None
    city_name: str | None
    status: str
    coalition: str | None
    reelection: bool


class AssetItem(BaseModel):
    id: uuid.UUID
    election_year: int
    category: str | None
    description: str
    declared_value: float


class RevenueItem(BaseModel):
    id: uuid.UUID
    election_year: int
    donor_name: str | None
    donor_type: str | None
    revenue_type: str | None
    amount: float
    received_at: str | None


class ExpenseItem(BaseModel):
    id: uuid.UUID
    election_year: int
    supplier_name: str | None
    expense_type: str | None
    description: str | None
    amount: float


class ResultItem(BaseModel):
    id: uuid.UUID
    election_year: int
    round: int
    votes: int
    vote_percentage: float | None
    result_status: str
    elected: bool


# --- Helper ---

async def _get_politician_id(slug: str, db: AsyncSession) -> uuid.UUID:
    """Resolve slug para politician ID."""
    result = await db.execute(
        select(Politician.id).where(
            Politician.slug == slug,
            Politician.is_public == True,
            Politician.deleted_at == None,
        )
    )
    pid = result.scalar_one_or_none()
    if not pid:
        raise NotFoundError(detail="Político não encontrado.")
    return pid


async def _get_candidacies_for_politician(
    politician_id: uuid.UUID, db: AsyncSession, year: int | None = None
):
    """Busca candidaturas vinculadas ao político."""
    query = select(Candidacy).where(Candidacy.politician_id == politician_id)
    if year:
        query = query.join(Election).where(Election.year == year)
    query = query.order_by(Candidacy.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


# --- Endpoints ---

@router.get("/candidacies")
async def get_candidacies(
    slug: str,
    election_year: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Lista candidaturas do político."""
    pid = await _get_politician_id(slug, db)
    query = (
        select(Candidacy, Election)
        .join(Election, Candidacy.election_id == Election.id)
        .where(Candidacy.politician_id == pid)
    )
    if election_year:
        query = query.where(Election.year == election_year)
    query = query.order_by(Election.year.desc())

    # Count
    count_q = select(sa_func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    # Paginate
    offset = (page - 1) * limit
    result = await db.execute(query.offset(offset).limit(limit))
    rows = result.all()

    items = []
    for cand, elec in rows:
        items.append(CandidacyItem(
            id=cand.id,
            election_year=elec.year,
            election_name=elec.name,
            position=cand.position.name if cand.position else None,
            party_acronym=cand.party.acronym if cand.party else None,
            ballot_name=cand.ballot_name,
            ballot_number=cand.ballot_number,
            state_code=cand.state_code,
            city_name=cand.city_name,
            status=cand.status,
            coalition=cand.coalition_name,
            reelection=cand.reelection,
        ))

    return {
        "data": items,
        "pagination": {"total": total, "page": page, "limit": limit},
        "metadata": MetadataResponse().model_dump(),
    }


@router.get("/assets")
async def get_assets(
    slug: str,
    election_year: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Lista bens declarados à Justiça Eleitoral."""
    pid = await _get_politician_id(slug, db)

    query = (
        select(CandidateAsset, Election.year)
        .join(Candidacy, CandidateAsset.candidacy_id == Candidacy.id)
        .join(Election, Candidacy.election_id == Election.id)
        .where(Candidacy.politician_id == pid)
    )
    if election_year:
        query = query.where(Election.year == election_year)
    query = query.order_by(Election.year.desc())

    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    rows = result.all()

    items = [
        AssetItem(
            id=asset.id,
            election_year=year,
            category=asset.category_name,
            description=asset.description,
            declared_value=float(asset.declared_value),
        )
        for asset, year in rows
    ]

    return {
        "data": items,
        "pagination": {"page": page, "limit": limit},
        "metadata": MetadataResponse().model_dump(),
        "disclaimer": (
            "Valores declarados à Justiça Eleitoral na eleição selecionada. "
            "Não representam necessariamente o patrimônio atual."
        ),
    }


@router.get("/campaign/revenues")
async def get_campaign_revenues(
    slug: str,
    election_year: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Lista receitas de campanha eleitoral."""
    pid = await _get_politician_id(slug, db)

    query = (
        select(CampaignRevenue, Election.year)
        .join(Candidacy, CampaignRevenue.candidacy_id == Candidacy.id)
        .join(Election, Candidacy.election_id == Election.id)
        .where(Candidacy.politician_id == pid)
    )
    if election_year:
        query = query.where(Election.year == election_year)
    query = query.order_by(Election.year.desc(), CampaignRevenue.amount.desc())

    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    rows = result.all()

    items = [
        RevenueItem(
            id=rev.id,
            election_year=year,
            donor_name=rev.donor_name,
            donor_type=rev.donor_type,
            revenue_type=rev.revenue_type,
            amount=float(rev.amount),
            received_at=str(rev.received_at) if rev.received_at else None,
        )
        for rev, year in rows
    ]

    return {
        "data": items,
        "pagination": {"page": page, "limit": limit},
        "metadata": MetadataResponse().model_dump(),
    }


@router.get("/campaign/expenses")
async def get_campaign_expenses(
    slug: str,
    election_year: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Lista despesas de campanha eleitoral."""
    pid = await _get_politician_id(slug, db)

    query = (
        select(CampaignExpense, Election.year)
        .join(Candidacy, CampaignExpense.candidacy_id == Candidacy.id)
        .join(Election, Candidacy.election_id == Election.id)
        .where(Candidacy.politician_id == pid)
    )
    if election_year:
        query = query.where(Election.year == election_year)
    query = query.order_by(Election.year.desc(), CampaignExpense.amount.desc())

    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    rows = result.all()

    items = [
        ExpenseItem(
            id=exp.id,
            election_year=year,
            supplier_name=exp.supplier_name,
            expense_type=exp.expense_type,
            description=exp.description,
            amount=float(exp.amount),
        )
        for exp, year in rows
    ]

    return {
        "data": items,
        "pagination": {"page": page, "limit": limit},
        "metadata": MetadataResponse().model_dump(),
    }


@router.get("/election-results")
async def get_election_results(
    slug: str,
    election_year: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Lista resultados eleitorais do político."""
    pid = await _get_politician_id(slug, db)

    query = (
        select(ElectionResult, Election.year)
        .join(Candidacy, ElectionResult.candidacy_id == Candidacy.id)
        .join(Election, Candidacy.election_id == Election.id)
        .where(Candidacy.politician_id == pid)
    )
    if election_year:
        query = query.where(Election.year == election_year)
    query = query.order_by(Election.year.desc())

    result = await db.execute(query)
    rows = result.all()

    items = [
        ResultItem(
            id=res.id,
            election_year=year,
            round=res.round,
            votes=res.votes,
            vote_percentage=res.vote_percentage,
            result_status=res.result_status,
            elected=res.elected,
        )
        for res, year in rows
    ]

    return {
        "data": items,
        "metadata": MetadataResponse().model_dump(),
    }
