"""
Coleta de notícias — Fluxo completo
Execute: python scripts/collect_news.py [politician_slug] [--classify]

Exemplos:
  python scripts/collect_news.py adriana-ventura
  python scripts/collect_news.py adriana-ventura --classify
  python scripts/collect_news.py all --limit 5
"""

import asyncio
import hashlib
import os
import sys
from datetime import UTC, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.politician import Politician
from app.models.news import NewsArticle, NewsMention, NewsClassification

settings = get_settings()
GDELT_API = "https://api.gdeltproject.org/api/v2/doc/doc"

SLUG = sys.argv[1] if len(sys.argv) > 1 else "all"
CLASSIFY = "--classify" in sys.argv
LIMIT = 5


def _parse_gdelt_date(date_str: str | None) -> datetime | None:
    """Parse GDELT date format: 20260620T151500Z"""
    if not date_str:
        return None
    try:
        from datetime import datetime as dt
        # Format: YYYYMMDDTHHMMSSz
        cleaned = date_str.replace("Z", "").replace("z", "")
        return dt.strptime(cleaned, "%Y%m%dT%H%M%S").replace(tzinfo=UTC)
    except (ValueError, AttributeError):
        return None


async def collect_gdelt(query: str, max_results: int = 20) -> list[dict]:
    """Fetch news from GDELT."""
    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": str(min(max_results, 75)),
        "format": "json",
        "sourcelang": "por",
        "sort": "DateDesc",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(GDELT_API, params=params)
            if resp.status_code != 200:
                print(f"  GDELT status: {resp.status_code}")
                return []
            data = resp.json()
            return data.get("articles", [])
        except Exception as e:
            print(f"  GDELT error: {e}")
            return []


async def save_articles(db: AsyncSession, articles: list[dict], politician: Politician) -> dict:
    """Save articles, deduplicate, create mentions."""
    stats = {"collected": 0, "duplicates": 0, "saved": 0}

    for art in articles:
        stats["collected"] += 1
        url = art.get("url", "")
        if not url:
            continue

        content_hash = hashlib.sha256(url.encode()).hexdigest()

        # Deduplication
        existing = await db.execute(
            select(NewsArticle.id).where(NewsArticle.content_hash == content_hash)
        )
        if existing.scalar_one_or_none():
            stats["duplicates"] += 1
            continue

        article = NewsArticle(
            provider="gdelt",
            external_id=hashlib.md5(url.encode()).hexdigest(),
            title=(art.get("title") or "")[:1000],
            canonical_url=url,
            original_url=url,
            image_url=art.get("socialimage"),
            language="pt",
            published_at=_parse_gdelt_date(art.get("seendate")),
            collected_at=datetime.now(UTC),
            content_hash=content_hash,
            status="collected",
        )
        db.add(article)
        await db.flush()

        # Create mention
        db.add(NewsMention(
            article_id=article.id,
            politician_id=politician.id,
            is_primary_subject=True,
            identity_confidence=0.7,  # Medium confidence from search query
            resolution_status="pending",
        ))
        stats["saved"] += 1

    await db.flush()
    return stats


async def classify_article(db: AsyncSession, article: NewsArticle, politician: Politician) -> bool:
    """Classify article using AI (DeepSeek)."""
    if not settings.openai_api_key:
        print("    ⚠ AI API key not configured, skipping classification")
        return False

    from app.integrations.ai.client import AiClient

    ai = AiClient()
    try:
        context = f"{politician.ballot_name or politician.full_name}, {politician.state_code}"
        result = await ai.classify_article(
            article_title=article.title,
            article_content=article.description or article.title,
            politician_name=politician.full_name,
            politician_context=context,
        )

        classification_data = result.get("classification", {})
        identity_data = result.get("politician_identity", {})
        metadata = result.get("_metadata", {})

        # Apply publication rules
        from app.integrations.news.publication_rules import apply_publication_rules
        decision = apply_publication_rules({
            "category": classification_data.get("category", "other"),
            "fact_type": classification_data.get("fact_type", "unclear"),
            "confidence": classification_data.get("confidence", 0),
            "identity_confidence": identity_data.get("confidence", 0),
            "reputational_impact": classification_data.get("reputational_impact", "neutral"),
            "evidence": result.get("evidence", []),
            "summary": result.get("summary", ""),
            "source_url": article.canonical_url,
        })

        review_status = "auto_approved" if decision.can_publish else "pending"

        classification = NewsClassification(
            article_id=article.id,
            politician_id=politician.id,
            sentiment=classification_data.get("sentiment", "neutral"),
            reputational_impact=classification_data.get("reputational_impact", "neutral"),
            impact_intensity=classification_data.get("impact_intensity", 0),
            category=classification_data.get("category", "other"),
            fact_type=classification_data.get("fact_type", "unclear"),
            confidence=classification_data.get("confidence", 0),
            summary=result.get("summary"),
            justification=result.get("justification"),
            evidence_json=result.get("evidence"),
            requires_human_review=decision.requires_review,
            review_reasons=decision.reasons,
            review_status=review_status,
            model_provider="deepseek",
            model_name=settings.openai_model,
            prompt_version="v1",
            tokens_used=(metadata.get("input_tokens", 0) + metadata.get("output_tokens", 0)),
            processing_time_ms=metadata.get("processing_time_ms"),
        )
        db.add(classification)

        article.status = "classified" if not decision.requires_review else "pending_review"
        await db.flush()
        return True

    except Exception as e:
        print(f"    ❌ Classification error: {type(e).__name__}: {str(e)[:80]}")
        return False
    finally:
        await ai.close()


async def main():
    print(f"\n{'='*60}")
    print(f"  COLETA DE NOTÍCIAS — IFB")
    print(f"  Político: {SLUG} | Classificar: {CLASSIFY}")
    print(f"{'='*60}\n")

    engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=2)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as db:
        # Get politicians
        if SLUG == "all":
            r = await db.execute(
                select(Politician).where(Politician.is_public == True, Politician.deleted_at == None)
                .order_by(Politician.full_name).limit(LIMIT)
            )
            politicians = list(r.scalars().all())
        else:
            r = await db.execute(
                select(Politician).where(Politician.slug == SLUG, Politician.is_public == True)
            )
            pol = r.scalar_one_or_none()
            if not pol:
                print(f"  ❌ Político não encontrado: {SLUG}")
                return
            politicians = [pol]

        print(f"  Políticos: {len(politicians)}")

        total_stats = {"collected": 0, "saved": 0, "duplicates": 0, "classified": 0}

        for pol in politicians:
            print(f"\n  [{pol.full_name}]")

            # Build search query
            query = f'"{pol.full_name}"'
            if pol.ballot_name and pol.ballot_name != pol.full_name:
                query += f' OR "{pol.ballot_name}"'

            # Collect from GDELT
            articles = await collect_gdelt(query, max_results=15)
            print(f"    GDELT: {len(articles)} artigos encontrados")

            # Save
            stats = await save_articles(db, articles, pol)
            total_stats["collected"] += stats["collected"]
            total_stats["saved"] += stats["saved"]
            total_stats["duplicates"] += stats["duplicates"]
            print(f"    Salvos: {stats['saved']}, Duplicados: {stats['duplicates']}")

            # Classify if requested
            if CLASSIFY and stats["saved"] > 0:
                # Get unclassified articles for this politician
                unclassified = await db.execute(
                    select(NewsArticle).join(NewsMention).where(
                        NewsMention.politician_id == pol.id,
                        NewsArticle.status == "collected",
                    ).limit(3)  # Limit to 3 per politician to control costs
                )
                for art in unclassified.scalars().all():
                    print(f"    Classificando: {art.title[:50]}...")
                    success = await classify_article(db, art, pol)
                    if success:
                        total_stats["classified"] += 1
                    await asyncio.sleep(1)  # Rate limit AI calls

            await asyncio.sleep(3)  # Rate limit GDELT (avoid 429)

        await db.commit()

    await engine.dispose()

    print(f"\n{'='*60}")
    print(f"  RESULTADO")
    print(f"{'='*60}")
    for k, v in total_stats.items():
        print(f"  {k}: {v}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
