"""Endpoint público de estatísticas gerais da plataforma."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.legislative import (
    CommitteeMembership,
    LegislativeProposition,
    LegislatorVote,
    ParliamentaryExpense,
)
from app.models.news import NewsArticle, NewsClassification, NewsMention
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


@router.get("/news/latest")
async def get_latest_news(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Retorna notícias aprovadas mais recentes (público)."""
    query = (
        select(NewsClassification, NewsArticle, Politician.full_name, Politician.slug)
        .join(NewsArticle, NewsClassification.article_id == NewsArticle.id)
        .join(NewsMention, NewsMention.article_id == NewsArticle.id)
        .join(Politician, NewsMention.politician_id == Politician.id)
        .where(
            NewsClassification.review_status.in_(["auto_approved", "approved"]),
            Politician.is_public == True,
        )
        .order_by(desc(NewsArticle.published_at))
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()

    items = [
        {
            "id": str(classification.id),
            "title": article.title,
            "source_url": article.canonical_url,
            "category": classification.category,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "politician_name": politician_name,
            "politician_slug": politician_slug,
            "summary": classification.summary,
        }
        for classification, article, politician_name, politician_slug in rows
    ]

    return {"items": items, "total": len(items)}
