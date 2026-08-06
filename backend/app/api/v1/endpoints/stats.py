"""Endpoint público de estatísticas gerais da plataforma."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.legislative import (
    CommitteeMembership,
    LegislativeProposition,
    LegislatorVote,
    ParliamentaryExpense,
)
from app.models.politician import Politician

router = APIRouter(tags=["Estatísticas"])


@router.get("/stats")
async def get_platform_stats(db: AsyncSession = Depends(get_db)):
    """Retorna indicadores públicos da plataforma (dados reais do banco)."""
    politicians = (
        await db.execute(
            select(func.count(Politician.id)).where(
                Politician.is_public == True, Politician.deleted_at == None
            )
        )
    ).scalar_one()

    propositions = (await db.execute(select(func.count(LegislativeProposition.id)))).scalar_one()

    votes = (await db.execute(select(func.count(LegislatorVote.id)))).scalar_one()

    committees = (await db.execute(select(func.count(CommitteeMembership.id)))).scalar_one()

    total_expenses = (
        await db.execute(select(func.coalesce(func.sum(ParliamentaryExpense.net_amount), 0)))
    ).scalar_one()

    return {
        "politicians": politicians,
        "propositions": propositions,
        "votes": votes,
        "committees": committees,
        "expenses_total": float(total_expenses),
    }
