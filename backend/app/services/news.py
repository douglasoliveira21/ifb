"""Serviço de coleta, processamento e classificação de notícias."""

import hashlib
import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.ai.client import AiClient
from app.integrations.news.providers import get_active_providers
from app.models.news import (
    AiUsageRecord,
    NewsArticle,
    NewsClassification,
    NewsCluster,
    NewsMention,
    NewsSource,
)
from app.models.politician import Politician, PoliticianAlias

logger = logging.getLogger(__name__)

# Sensitive categories requiring human review
SENSITIVE_CATEGORIES = {
    "judicial", "investigation", "corruption", "charge_filed",
    "charge_accepted", "conviction_first_instance", "conviction_appealable",
    "final_conviction",
}

NEWS_AUTO_PUBLISH_MIN_CONFIDENCE = 0.92
NEWS_IDENTITY_MIN_CONFIDENCE = 0.95


class NewsService:
    """Orquestra coleta, deduplicação, classificação e publicação de notícias."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def collect_for_politician(self, politician_id: uuid.UUID) -> dict:
        """Coleta notícias para um político específico."""
        # Get politician details for query building
        result = await self.db.execute(
            select(Politician).where(Politician.id == politician_id)
        )
        politician = result.scalar_one_or_none()
        if not politician:
            return {"error": "Politician not found"}

        # Build search query
        query = self._build_search_query(politician)
        providers = get_active_providers()

        stats = {"collected": 0, "duplicates": 0, "errors": 0}

        for provider in providers:
            try:
                articles = await provider.search(query, max_results=30)
                for article_data in articles:
                    try:
                        saved = await self._save_article(article_data, politician)
                        if saved:
                            stats["collected"] += 1
                        else:
                            stats["duplicates"] += 1
                    except Exception as e:
                        stats["errors"] += 1
                        logger.warning("Error saving article: %s", e)
            except Exception as e:
                logger.error("Provider %s failed: %s", provider.provider_name, e)
                stats["errors"] += 1

        await self.db.flush()
        return stats

    def _build_search_query(self, politician: Politician) -> str:
        """Constrói query de busca usando nome e aliases."""
        parts = [f'"{politician.full_name}"']
        if politician.ballot_name and politician.ballot_name != politician.full_name:
            parts.append(f'"{politician.ballot_name}"')
        return " OR ".join(parts)

    async def _save_article(self, data: dict, politician: Politician) -> bool:
        """Salva artigo se não for duplicado. Retorna True se novo."""
        url = data.get("url", "")
        content_hash = hashlib.sha256(url.encode()).hexdigest()

        # Check duplicate by content_hash
        existing = await self.db.execute(
            select(NewsArticle).where(NewsArticle.content_hash == content_hash)
        )
        if existing.scalar_one_or_none():
            return False

        # Resolve or create source
        domain = data.get("source_domain", "")

        article = NewsArticle(
            provider=data.get("provider", "unknown"),
            external_id=data.get("external_id"),
            title=data.get("title", "")[:1000],
            description=data.get("description"),
            canonical_url=url,
            original_url=url,
            image_url=data.get("image_url"),
            author=data.get("author"),
            language=data.get("language", "pt"),
            published_at=data.get("published_at"),
            content_hash=content_hash,
            status="collected",
        )
        self.db.add(article)
        await self.db.flush()

        # Create mention
        mention = NewsMention(
            article_id=article.id,
            politician_id=politician.id,
            is_primary_subject=True,
            identity_confidence=0.0,  # Will be set by AI
            resolution_status="pending",
        )
        self.db.add(mention)
        return True

    async def classify_article(
        self, article_id: uuid.UUID, politician_id: uuid.UUID
    ) -> NewsClassification | None:
        """Classifica artigo usando IA e aplica regras de segurança."""
        # Get article
        art_result = await self.db.execute(
            select(NewsArticle).where(NewsArticle.id == article_id)
        )
        article = art_result.scalar_one_or_none()
        if not article:
            return None

        # Get politician
        pol_result = await self.db.execute(
            select(Politician).where(Politician.id == politician_id)
        )
        politician = pol_result.scalar_one_or_none()
        if not politician:
            return None

        # Call AI
        ai_client = AiClient()
        try:
            context = f"{politician.ballot_name or ''}, {politician.state_code or ''}"
            result = await ai_client.classify_article(
                article_title=article.title,
                article_content=article.description or article.content_excerpt or "",
                politician_name=politician.full_name,
                politician_context=context,
            )
        except Exception as e:
            logger.error("AI classification failed for article %s: %s", article_id, e)
            return None
        finally:
            await ai_client.close()

        # Parse result
        classification_data = result.get("classification", {})
        identity_data = result.get("politician_identity", {})

        # Determine if human review is needed
        requires_review = result.get("requires_human_review", True)
        review_reasons = result.get("review_reasons", [])

        # Apply safety rules
        category = classification_data.get("category", "other")
        confidence = classification_data.get("confidence", 0.0)
        identity_conf = identity_data.get("confidence", 0.0)

        if category in SENSITIVE_CATEGORIES:
            requires_review = True
            if "sensitive_category" not in review_reasons:
                review_reasons.append("sensitive_category")

        if confidence < NEWS_AUTO_PUBLISH_MIN_CONFIDENCE:
            requires_review = True
            if "low_confidence" not in review_reasons:
                review_reasons.append("low_confidence")

        if identity_conf < NEWS_IDENTITY_MIN_CONFIDENCE:
            requires_review = True
            if "identity_uncertain" not in review_reasons:
                review_reasons.append("identity_uncertain")

        # Determine review status
        review_status = "pending" if requires_review else "auto_approved"

        # Save classification
        metadata = result.get("_metadata", {})
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
            model_provider="openai",
            model_name=metadata.get("model", settings.openai_model),
            prompt_version=metadata.get("prompt_version", "v1"),
            tokens_used=(metadata.get("input_tokens", 0) + metadata.get("output_tokens", 0)),
            processing_time_ms=metadata.get("processing_time_ms"),
        )
        self.db.add(classification)

        # Update mention confidence
        mention_result = await self.db.execute(
            select(NewsMention).where(
                NewsMention.article_id == article_id,
                NewsMention.politician_id == politician_id,
            )
        )
        mention = mention_result.scalar_one_or_none()
        if mention:
            mention.identity_confidence = identity_conf
            mention.is_primary_subject = identity_data.get("is_primary_subject", False)
            mention.resolution_status = "confirmed" if identity_conf >= 0.95 else "pending"

        # Update article status
        article.status = "classified" if not requires_review else "pending_review"

        # Record AI usage
        usage = AiUsageRecord(
            provider="openai",
            model=metadata.get("model", settings.openai_model),
            operation="classify_article",
            input_tokens=metadata.get("input_tokens", 0),
            output_tokens=metadata.get("output_tokens", 0),
            estimated_cost=self._estimate_cost(metadata),
            article_id=article_id,
            politician_id=politician_id,
        )
        self.db.add(usage)

        await self.db.flush()
        return classification

    @staticmethod
    def _estimate_cost(metadata: dict) -> float:
        """Estima custo da chamada de IA (USD)."""
        input_t = metadata.get("input_tokens", 0)
        output_t = metadata.get("output_tokens", 0)
        # gpt-4o-mini pricing approximation
        return (input_t * 0.00015 + output_t * 0.0006) / 1000
