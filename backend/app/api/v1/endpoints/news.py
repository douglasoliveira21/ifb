"""API pública e administrativa de notícias."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import (
    get_audit_service,
    get_client_ip,
    get_current_user,
    require_role,
)
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.news import (
    NewsArticle,
    NewsClassification,
    NewsContestation,
    NewsMention,
)
from app.models.politician import Politician
from app.models.user import User
from app.schemas.auth import MessageResponse

router = APIRouter(tags=["Notícias"])


# --- Public endpoints ---

@router.get("/politicians/{slug}/news")
async def get_politician_news(
    slug: str,
    impact: str | None = Query(None),
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Lista notícias classificadas de um político."""
    pol_result = await db.execute(
        select(Politician.id).where(
            Politician.slug == slug, Politician.is_public == True, Politician.deleted_at == None
        )
    )
    politician_id = pol_result.scalar_one_or_none()
    if not politician_id:
        raise NotFoundError(detail="Político não encontrado.")

    query = (
        select(NewsClassification, NewsArticle)
        .join(NewsArticle, NewsClassification.article_id == NewsArticle.id)
        .where(
            NewsClassification.politician_id == politician_id,
            NewsClassification.review_status.in_(["auto_approved", "approved"]),
        )
    )
    if impact:
        query = query.where(NewsClassification.reputational_impact == impact)
    if category:
        query = query.where(NewsClassification.category == category)

    query = query.order_by(desc(NewsArticle.published_at))
    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    rows = result.all()

    items = [
        {
            "id": str(classification.id),
            "title": article.title,
            "source_url": article.canonical_url,
            "source_domain": article.provider,
            "image_url": article.image_url,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "category": classification.category,
            "reputational_impact": classification.reputational_impact,
            "impact_intensity": classification.impact_intensity,
            "sentiment": classification.sentiment,
            "summary": classification.summary,
            "confidence": classification.confidence,
            "fact_type": classification.fact_type,
        }
        for classification, article in rows
    ]

    return {
        "data": items,
        "pagination": {"page": page, "limit": limit},
        "metadata": {
            "source": "Fontes jornalísticas públicas",
            "classification_method": "Inteligência artificial com revisão humana",
            "disclaimer": (
                "A classificação de impacto é produzida com auxílio automatizado. "
                "Não representa comprovação de culpa, inocência ou avaliação definitiva."
            ),
        },
    }


@router.get("/politicians/{slug}/news-summary")
async def get_politician_news_summary(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Resumo de notícias do político (contadores por impacto)."""
    pol_result = await db.execute(
        select(Politician.id).where(
            Politician.slug == slug, Politician.is_public == True, Politician.deleted_at == None
        )
    )
    politician_id = pol_result.scalar_one_or_none()
    if not politician_id:
        raise NotFoundError(detail="Político não encontrado.")

    # Count by impact
    counts = {}
    for impact in ["positive", "negative", "neutral", "mixed", "inconclusive"]:
        result = await db.execute(
            select(func.count(NewsClassification.id)).where(
                NewsClassification.politician_id == politician_id,
                NewsClassification.reputational_impact == impact,
                NewsClassification.review_status.in_(["auto_approved", "approved"]),
            )
        )
        counts[impact] = result.scalar_one()

    total = sum(counts.values())

    return {
        "total_articles": total,
        **counts,
        "disclaimer": "Quantidade de notícias não representa aprovação popular.",
    }


# --- Contestation ---

class ContestRequest(BaseModel):
    reason: str
    description: str | None = None


@router.post("/news/{article_id}/contest", response_model=MessageResponse)
async def contest_classification(
    article_id: uuid.UUID,
    data: ContestRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Contesta classificação de uma notícia."""
    # Verify article exists
    art_result = await db.execute(select(NewsArticle).where(NewsArticle.id == article_id))
    if not art_result.scalar_one_or_none():
        raise NotFoundError(detail="Notícia não encontrada.")

    contestation = NewsContestation(
        article_id=article_id,
        user_id=user.id,
        reason=data.reason,
        description=data.description,
        status="pending",
    )
    db.add(contestation)
    await db.flush()
    return MessageResponse(message="Contestação registrada para análise.")


# --- Admin endpoints ---

@router.get("/admin/news/review-queue")
async def get_review_queue(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("analyst")),
):
    """Fila de revisão humana."""
    query = (
        select(NewsClassification, NewsArticle)
        .join(NewsArticle, NewsClassification.article_id == NewsArticle.id)
        .where(NewsClassification.review_status == "pending")
        .order_by(desc(NewsClassification.created_at))
    )
    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    rows = result.all()

    items = [
        {
            "classification_id": str(c.id),
            "article_title": a.title,
            "article_url": a.canonical_url,
            "category": c.category,
            "impact": c.reputational_impact,
            "intensity": c.impact_intensity,
            "confidence": c.confidence,
            "summary": c.summary,
            "justification": c.justification,
            "review_reasons": c.review_reasons,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c, a in rows
    ]

    return {"data": items, "page": page, "limit": limit}


@router.post("/admin/news/{classification_id}/approve", response_model=MessageResponse)
async def approve_classification(
    classification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("analyst")),
):
    """Aprova classificação para publicação."""
    result = await db.execute(
        select(NewsClassification).where(NewsClassification.id == classification_id)
    )
    classification = result.scalar_one_or_none()
    if not classification:
        raise NotFoundError(detail="Classificação não encontrada.")

    classification.review_status = "approved"
    classification.reviewed_by = user.email
    classification.reviewed_at = datetime.now(UTC)
    await db.flush()
    return MessageResponse(message="Classificação aprovada.")


@router.post("/admin/news/{classification_id}/reject", response_model=MessageResponse)
async def reject_classification(
    classification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("analyst")),
):
    """Rejeita classificação."""
    result = await db.execute(
        select(NewsClassification).where(NewsClassification.id == classification_id)
    )
    classification = result.scalar_one_or_none()
    if not classification:
        raise NotFoundError(detail="Classificação não encontrada.")

    classification.review_status = "rejected"
    classification.reviewed_by = user.email
    classification.reviewed_at = datetime.now(UTC)
    await db.flush()
    return MessageResponse(message="Classificação rejeitada.")
