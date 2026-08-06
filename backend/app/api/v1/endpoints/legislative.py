"""API pública legislativa — proposições, votações, presença, gastos."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, and_, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.legislative import (
    CommitteeMembership,
    Legislator,
    LegislativeCommittee,
    LegislativeProposition,
    LegislativeSpeech,
    LegislativeVoteEvent,
    LegislatorVote,
    ParliamentaryExpense,
    PoliticianLegislativeProfile,
    PropositionAuthor,
    SessionAttendance,
)
from app.models.politician import Politician

router = APIRouter(prefix="/politicians/{slug}", tags=["Dados Legislativos"])


# --- Helpers ---

async def _get_legislator_ids(slug: str, db: AsyncSession) -> list[uuid.UUID]:
    """Resolve slug do político para IDs de parlamentar vinculado."""
    pol_result = await db.execute(
        select(Politician.id).where(
            Politician.slug == slug, Politician.is_public == True, Politician.deleted_at == None
        )
    )
    politician_id = pol_result.scalar_one_or_none()
    if not politician_id:
        raise NotFoundError(detail="Político não encontrado.")

    profiles = await db.execute(
        select(PoliticianLegislativeProfile.legislator_id).where(
            PoliticianLegislativeProfile.politician_id == politician_id,
            PoliticianLegislativeProfile.status.in_(["confirmed", "probable"]),
        )
    )
    return [row for row in profiles.scalars().all()]


class LegislativeMetadata(BaseModel):
    source: str = "Câmara dos Deputados / Senado Federal"
    source_url: str | None = None
    collected_at: datetime | None = None
    availability: str = "available"


# --- Endpoints ---

@router.get("/legislative-profile")
async def get_legislative_profile(
    slug: str, db: AsyncSession = Depends(get_db)
):
    """Retorna perfil legislativo do político."""
    pol_result = await db.execute(
        select(Politician.id).where(
            Politician.slug == slug, Politician.is_public == True, Politician.deleted_at == None
        )
    )
    politician_id = pol_result.scalar_one_or_none()
    if not politician_id:
        raise NotFoundError(detail="Político não encontrado.")

    profiles = await db.execute(
        select(PoliticianLegislativeProfile, Legislator)
        .join(Legislator, PoliticianLegislativeProfile.legislator_id == Legislator.id)
        .where(PoliticianLegislativeProfile.politician_id == politician_id)
    )
    rows = profiles.all()

    items = []
    for profile, legislator in rows:
        items.append({
            "house": legislator.house_id,
            "external_id": legislator.external_id,
            "full_name": legislator.full_name,
            "party": legislator.party_acronym,
            "state": legislator.state_code,
            "status": legislator.status,
            "match_status": profile.status,
            "confidence": profile.match_confidence,
        })

    return {"data": items, "metadata": LegislativeMetadata().model_dump()}


@router.get("/propositions")
async def get_propositions(
    slug: str,
    year: int | None = Query(None),
    type: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Lista proposições do parlamentar."""
    legislator_ids = await _get_legislator_ids(slug, db)
    if not legislator_ids:
        return {"data": [], "pagination": {"total": 0, "page": page, "limit": limit},
                "metadata": LegislativeMetadata(availability="not_available").model_dump()}

    query = (
        select(LegislativeProposition)
        .join(PropositionAuthor)
        .where(PropositionAuthor.legislator_id.in_(legislator_ids))
    )
    if year:
        query = query.where(LegislativeProposition.year == year)
    if type:
        query = query.where(LegislativeProposition.type_acronym == type.upper())
    query = query.order_by(LegislativeProposition.presentation_date.desc())

    count_q = select(sa_func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    props = result.scalars().all()

    items = [
        {
            "id": p.id, "type": p.type_acronym, "number": p.number,
            "year": p.year, "title": p.title, "summary": p.summary,
            "status": p.status, "presentation_date": str(p.presentation_date) if p.presentation_date else None,
            "source_url": p.source_url,
        }
        for p in props
    ]

    return {
        "data": items,
        "pagination": {"total": total, "page": page, "limit": limit},
        "metadata": LegislativeMetadata().model_dump(),
    }


@router.get("/votes")
async def get_votes(
    slug: str,
    year: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Lista votações do parlamentar com votos individuais."""
    legislator_ids = await _get_legislator_ids(slug, db)
    if not legislator_ids:
        return {"data": [], "metadata": LegislativeMetadata(availability="not_available").model_dump()}

    query = (
        select(LegislatorVote, LegislativeVoteEvent)
        .join(LegislativeVoteEvent, LegislatorVote.vote_event_id == LegislativeVoteEvent.id)
        .where(LegislatorVote.legislator_id.in_(legislator_ids))
    )
    if year:
        query = query.where(sa_func.extract("year", LegislativeVoteEvent.date) == year)
    query = query.order_by(LegislativeVoteEvent.date.desc())

    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    rows = result.all()

    items = [
        {
            "vote_event_id": event.id,
            "date": str(event.date) if event.date else None,
            "description": event.description,
            "result": event.result,
            "vote": vote.normalized_vote,
            "original_vote": vote.original_vote,
            "party_at_vote": vote.party_at_vote,
            "source_url": event.source_url,
        }
        for vote, event in rows
    ]

    return {"data": items, "pagination": {"page": page, "limit": limit},
            "metadata": LegislativeMetadata().model_dump()}


@router.get("/attendance")
async def get_attendance(
    slug: str,
    year: int | None = Query(None),
    month: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Presença em sessões legislativas."""
    legislator_ids = await _get_legislator_ids(slug, db)
    if not legislator_ids:
        return {"data": [], "summary": {}, "metadata": LegislativeMetadata(availability="not_available").model_dump()}

    query = select(SessionAttendance).where(
        SessionAttendance.legislator_id.in_(legislator_ids)
    )
    if year:
        query = query.where(sa_func.extract("year", SessionAttendance.session_date) == year)
    if month:
        query = query.where(sa_func.extract("month", SessionAttendance.session_date) == month)

    result = await db.execute(query.order_by(SessionAttendance.session_date.desc()))
    records = result.scalars().all()

    # Calculate summary
    total = len(records)
    present = sum(1 for r in records if r.attendance_status == "present")
    absent_justified = sum(1 for r in records if r.attendance_status == "absent_justified")
    absent = sum(1 for r in records if r.attendance_status == "absent")

    return {
        "data": [
            {
                "date": str(r.session_date) if r.session_date else None,
                "session_type": r.session_type,
                "status": r.attendance_status,
                "justification": r.justification,
            }
            for r in records[:100]  # Limit to 100 most recent
        ],
        "summary": {
            "total_sessions": total,
            "present": present,
            "absent_justified": absent_justified,
            "absent": absent,
            "attendance_rate": round(present / total * 100, 1) if total > 0 else None,
        },
        "metadata": LegislativeMetadata().model_dump(),
        "methodology_url": "/api/v1/methodologies/attendance",
    }


@router.get("/parliamentary-expenses")
async def get_parliamentary_expenses(
    slug: str,
    year: int | None = Query(None),
    month: int | None = Query(None),
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Gastos parlamentares (CEAP/cota)."""
    legislator_ids = await _get_legislator_ids(slug, db)
    if not legislator_ids:
        return {"data": [], "metadata": LegislativeMetadata(availability="not_available").model_dump()}

    query = select(ParliamentaryExpense).where(
        ParliamentaryExpense.legislator_id.in_(legislator_ids)
    )
    if year:
        query = query.where(ParliamentaryExpense.year == year)
    if month:
        query = query.where(ParliamentaryExpense.month == month)
    if category:
        query = query.where(ParliamentaryExpense.category.ilike(f"%{category}%"))
    query = query.order_by(
        ParliamentaryExpense.year.desc(),
        ParliamentaryExpense.month.desc(),
        ParliamentaryExpense.net_amount.desc(),
    )

    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    expenses = result.scalars().all()

    # Aggregates
    total_query = select(
        sa_func.sum(ParliamentaryExpense.net_amount)
    ).where(ParliamentaryExpense.legislator_id.in_(legislator_ids))
    if year:
        total_query = total_query.where(ParliamentaryExpense.year == year)
    total_amount = (await db.execute(total_query)).scalar_one_or_none() or 0

    items = [
        {
            "id": e.id, "year": e.year, "month": e.month,
            "category": e.category, "supplier_name": e.supplier_name,
            "gross_amount": float(e.gross_amount),
            "net_amount": float(e.net_amount),
            "document_url": e.document_url,
        }
        for e in expenses
    ]

    return {
        "data": items,
        "aggregates": {"total_net_amount": float(total_amount)},
        "pagination": {"page": page, "limit": limit},
        "metadata": LegislativeMetadata().model_dump(),
    }


@router.get("/committees")
async def get_committees(
    slug: str, db: AsyncSession = Depends(get_db)
):
    """Comissões do parlamentar."""
    legislator_ids = await _get_legislator_ids(slug, db)
    if not legislator_ids:
        return {"data": [], "metadata": LegislativeMetadata(availability="not_available").model_dump()}

    query = (
        select(CommitteeMembership, LegislativeCommittee)
        .join(LegislativeCommittee, CommitteeMembership.committee_id == LegislativeCommittee.id)
        .where(CommitteeMembership.legislator_id.in_(legislator_ids))
    )
    result = await db.execute(query)
    rows = result.all()

    items = [
        {
            "committee_name": comm.name,
            "acronym": comm.acronym,
            "role": membership.role,
            "started_at": str(membership.started_at) if membership.started_at else None,
            "ended_at": str(membership.ended_at) if membership.ended_at else None,
        }
        for membership, comm in rows
    ]

    return {"data": items, "metadata": LegislativeMetadata().model_dump()}


@router.get("/speeches")
async def get_speeches(
    slug: str,
    year: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Discursos do parlamentar."""
    legislator_ids = await _get_legislator_ids(slug, db)
    if not legislator_ids:
        return {"data": [], "metadata": LegislativeMetadata(availability="not_available").model_dump()}

    query = select(LegislativeSpeech).where(
        LegislativeSpeech.legislator_id.in_(legislator_ids)
    )
    if year:
        query = query.where(sa_func.extract("year", LegislativeSpeech.date) == year)
    query = query.order_by(LegislativeSpeech.date.desc())

    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    speeches = result.scalars().all()

    items = [
        {
            "id": s.id,
            "date": str(s.date) if s.date else None,
            "session_type": s.session_type,
            "summary": s.summary,
            "full_text_url": s.full_text_url,
            "source_url": s.source_url,
        }
        for s in speeches
    ]

    return {"data": items, "pagination": {"page": page, "limit": limit},
            "metadata": LegislativeMetadata().model_dump()}
