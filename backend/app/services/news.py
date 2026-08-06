"""Serviço de coleta, processamento e classificação de notícias."""

import hashlib
import logging
import re
import uuid
from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.integrations.ai.client import AiClient
from app.integrations.news.providers import (
    extract_domain,
    get_active_providers,
    normalize_url,
    parse_published_at,
)
from app.integrations.news.publication_rules import apply_publication_rules
from app.models.news import (
    AiUsageRecord,
    NewsArticle,
    NewsClassification,
    NewsMention,
    NewsSource,
)
from app.models.politician import Politician

logger = logging.getLogger(__name__)
settings = get_settings()

SENSITIVE_CATEGORIES = {
    "judicial",
    "investigation",
    "corruption",
    "charge_filed",
    "charge_accepted",
    "conviction_first_instance",
    "conviction_appealable",
    "final_conviction",
}
NEWS_AUTO_PUBLISH_MIN_CONFIDENCE = 0.92
NEWS_IDENTITY_MIN_CONFIDENCE = 0.95
GOOGLE_NEWS_DOMAIN = "news.google.com"


class NewsService:
    """Orquestra coleta, deduplicação, classificação e publicação de notícias."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def collect_for_politician(self, politician_id: uuid.UUID) -> dict:
        """Coleta notícias para um político específico, sem publicá-las."""
        result = await self.db.execute(
            select(Politician).where(Politician.id == politician_id)
        )
        politician = result.scalar_one_or_none()
        if not politician:
            return {"error": "Politician not found"}

        query = self._build_search_query(politician)
        stats = {"collected": 0, "duplicates": 0, "errors": 0}

        for provider in get_active_providers():
            try:
                articles = await provider.search(query, max_results=30)
                for article_data in articles:
                    try:
                        saved = await self._save_article(article_data, politician)
                        if saved:
                            stats["collected"] += 1
                        else:
                            stats["duplicates"] += 1
                    except Exception as exc:
                        stats["errors"] += 1
                        logger.warning(
                            "Error saving article from %s: %s",
                            provider.provider_name,
                            exc,
                        )
            except Exception as exc:
                logger.error("Provider %s failed: %s", provider.provider_name, exc)
                stats["errors"] += 1

        await self.db.flush()
        return stats

    @staticmethod
    def _build_search_query(politician: Politician) -> str:
        """Constrói query de busca usando nome e nome de urna."""
        parts = [f'"{politician.full_name}"']
        if politician.ballot_name and politician.ballot_name != politician.full_name:
            parts.append(f'"{politician.ballot_name}"')
        return " OR ".join(parts)

    @staticmethod
    def _stable_article_hash(
        canonical_url: str,
        source_domain: str | None,
        title: str,
        published_at: datetime | None,
    ) -> str:
        """Gera chave de idempotência a partir da URL canônica ou fallback estável."""
        domain = extract_domain(canonical_url)
        if canonical_url and domain != GOOGLE_NEWS_DOMAIN:
            value = canonical_url
        else:
            normalized_title = re.sub(r"\s+", " ", title.casefold()).strip()
            published_key = published_at.isoformat() if published_at else ""
            value = f"{source_domain or ''}|{normalized_title}|{published_key}"
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    async def _get_or_create_source(
        self,
        domain: str | None,
        name: str | None,
        provider: str,
    ) -> NewsSource | None:
        """Associa o artigo a uma fonte jornalística identificada pelo domínio."""
        if not domain:
            return None

        normalized_domain = domain.lower().strip().removeprefix("www.")
        result = await self.db.execute(
            select(NewsSource).where(NewsSource.domain == normalized_domain)
        )
        source = result.scalar_one_or_none()
        if source:
            return source

        source = NewsSource(
            name=(name or normalized_domain)[:255],
            domain=normalized_domain,
            provider=provider,
            source_type="journalistic",
            country="BR",
            language="pt",
            credibility_status="unknown",
        )
        self.db.add(source)
        await self.db.flush()
        return source

    async def _save_article(self, data: dict, politician: Politician) -> bool:
        """Persiste artigo normalizado e cria uma menção pendente de confirmação."""
        original_url = normalize_url(data.get("original_url") or data.get("url"))
        canonical_url = normalize_url(data.get("canonical_url") or data.get("url"))
        if not canonical_url:
            return False

        source_domain = (
            extract_domain(canonical_url)
            or extract_domain(data.get("source_url"))
            or data.get("source_domain")
        )
        if source_domain:
            source_domain = source_domain.lower().strip().removeprefix("www.")

        title = (data.get("title") or "").strip()
        published_at = parse_published_at(data.get("published_at"))
        content_hash = self._stable_article_hash(
            canonical_url,
            source_domain,
            title,
            published_at,
        )

        existing = await self.db.execute(
            select(NewsArticle.id).where(
                or_(
                    NewsArticle.content_hash == content_hash,
                    NewsArticle.canonical_url == canonical_url,
                )
            )
        )
        if existing.scalar_one_or_none():
            return False

        source = await self._get_or_create_source(
            source_domain,
            data.get("source_name"),
            data.get("provider", "unknown"),
        )
        article = NewsArticle(
            source_id=source.id if source else None,
            provider=data.get("provider", "unknown"),
            external_id=data.get("external_id"),
            title=title[:1000],
            description=data.get("description"),
            canonical_url=canonical_url,
            original_url=original_url or canonical_url,
            image_url=data.get("image_url"),
            author=data.get("author"),
            language=data.get("language", "pt"),
            published_at=published_at,
            content_hash=content_hash,
            status="collected",
        )
        self.db.add(article)
        await self.db.flush()

        self.db.add(
            NewsMention(
                article_id=article.id,
                politician_id=politician.id,
                is_primary_subject=True,
                identity_confidence=0.0,
                resolution_status="pending",
            )
        )
        return True

    async def classify_article(
        self, article_id: uuid.UUID, politician_id: uuid.UUID
    ) -> NewsClassification | None:
        """Classifica artigo com IA e aplica regras determinísticas de publicação."""
        art_result = await self.db.execute(
            select(NewsArticle).where(NewsArticle.id == article_id)
        )
        article = art_result.scalar_one_or_none()
        if not article:
            return None

        pol_result = await self.db.execute(
            select(Politician).where(Politician.id == politician_id)
        )
        politician = pol_result.scalar_one_or_none()
        if not politician:
            return None

        ai_client = AiClient()
        try:
            context = f"{politician.ballot_name or ''}, {politician.state_code or ''}"
            result = await ai_client.classify_article(
                article_title=article.title,
                article_content=article.description or article.content_excerpt or "",
                politician_name=politician.full_name,
                politician_context=context,
            )
        except Exception as exc:
            logger.error("AI classification failed for article %s: %s", article_id, exc)
            return None
        finally:
            await ai_client.close()

        classification_data = result.get("classification", {})
        identity_data = result.get("politician_identity", {})
        metadata = result.get("_metadata", {})
        category = classification_data.get("category", "other")
        confidence = classification_data.get("confidence", 0.0)
        identity_confidence = identity_data.get("confidence", 0.0)
        review_reasons = list(result.get("review_reasons") or [])
        requires_review = bool(result.get("requires_human_review", True))

        decision = apply_publication_rules(
            {
                "category": category,
                "fact_type": classification_data.get("fact_type", "unclear"),
                "confidence": confidence,
                "identity_confidence": identity_confidence,
                "reputational_impact": classification_data.get(
                    "reputational_impact", "neutral"
                ),
                "evidence": result.get("evidence", []),
                "summary": result.get("summary", ""),
                "source_url": article.canonical_url,
            }
        )
        requires_review = requires_review or decision.requires_review or not decision.can_publish
        review_reasons = list(dict.fromkeys([*review_reasons, *decision.reasons]))

        if category in SENSITIVE_CATEGORIES and "sensitive_category" not in review_reasons:
            review_reasons.append("sensitive_category")
        if confidence < NEWS_AUTO_PUBLISH_MIN_CONFIDENCE and "low_confidence" not in review_reasons:
            review_reasons.append("low_confidence")
        if (
            identity_confidence < NEWS_IDENTITY_MIN_CONFIDENCE
            and "identity_uncertain" not in review_reasons
        ):
            review_reasons.append("identity_uncertain")
            requires_review = True

        review_status = "pending" if requires_review else "auto_approved"
        provider_name = (
            "deepseek" if "deepseek" in settings.openai_api_base_url.lower() else "openai"
        )
        classification = NewsClassification(
            article_id=article_id,
            politician_id=politician_id,
            sentiment=classification_data.get("sentiment", "neutral"),
            reputational_impact=classification_data.get("reputational_impact", "neutral"),
            impact_intensity=classification_data.get("impact_intensity", 0),
            category=category,
            fact_type=classification_data.get("fact_type", "unclear"),
            confidence=confidence,
            summary=result.get("summary"),
            justification=result.get("justification"),
            evidence_json=result.get("evidence"),
            requires_human_review=requires_review,
            review_reasons=review_reasons,
            review_status=review_status,
            model_provider=provider_name,
            model_name=metadata.get("model", settings.openai_model),
            prompt_version=metadata.get("prompt_version", "v1"),
            tokens_used=(metadata.get("input_tokens", 0) + metadata.get("output_tokens", 0)),
            processing_time_ms=metadata.get("processing_time_ms"),
        )
        self.db.add(classification)

        mention_result = await self.db.execute(
            select(NewsMention).where(
                NewsMention.article_id == article_id,
                NewsMention.politician_id == politician_id,
            )
        )
        mention = mention_result.scalar_one_or_none()
        if mention:
            mention.identity_confidence = identity_confidence
            mention.is_primary_subject = identity_data.get("is_primary_subject", False)
            mention.resolution_status = (
                "confirmed" if identity_confidence >= NEWS_IDENTITY_MIN_CONFIDENCE else "pending"
            )

        article.status = "classified" if not requires_review else "pending_review"
        self.db.add(
            AiUsageRecord(
                provider=provider_name,
                model=metadata.get("model", settings.openai_model),
                operation="classify_article",
                input_tokens=metadata.get("input_tokens", 0),
                output_tokens=metadata.get("output_tokens", 0),
                estimated_cost=self._estimate_cost(metadata),
                article_id=article_id,
                politician_id=politician_id,
            )
        )
        await self.db.flush()
        return classification

    @staticmethod
    def _estimate_cost(metadata: dict) -> float:
        """Estima custo da chamada de IA (USD)."""
        input_tokens = metadata.get("input_tokens", 0)
        output_tokens = metadata.get("output_tokens", 0)
        return (input_tokens * 0.00015 + output_tokens * 0.0006) / 1000
