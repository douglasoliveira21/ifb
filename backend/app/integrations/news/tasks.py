"""Celery tasks para coleta e classificação de notícias."""

import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="news.collect_for_politician",
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    time_limit=300,
    soft_time_limit=270,
    queue="news-collect",
)
def task_collect_for_politician(self, politician_id: str):
    """Coleta notícias para um político específico."""
    import uuid
    from app.core.database import async_session_factory
    from app.services.news import NewsService

    async def _run():
        async with async_session_factory() as db:
            service = NewsService(db)
            stats = await service.collect_for_politician(uuid.UUID(politician_id))
            await db.commit()
            return stats

    try:
        stats = asyncio.run(_run())
        logger.info("News collection for %s: %s", politician_id, stats)
        return stats
    except Exception as exc:
        logger.error("News collection failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(
    name="news.classify_article",
    bind=True,
    max_retries=1,
    default_retry_delay=120,
    time_limit=120,
    soft_time_limit=100,
    queue="news-ai",
)
def task_classify_article(self, article_id: str, politician_id: str):
    """Classifica uma notícia usando IA."""
    import uuid
    from app.core.database import async_session_factory
    from app.services.news import NewsService

    async def _run():
        async with async_session_factory() as db:
            service = NewsService(db)
            result = await service.classify_article(
                uuid.UUID(article_id), uuid.UUID(politician_id)
            )
            await db.commit()
            return result is not None

    try:
        success = asyncio.run(_run())
        logger.info("Article %s classified: %s", article_id, success)
        return {"article_id": article_id, "classified": success}
    except Exception as exc:
        logger.error("Classification failed for %s: %s", article_id, exc)
        raise self.retry(exc=exc)


@celery_app.task(
    name="news.collect_all_active_politicians",
    time_limit=3600,
    queue="news-collect",
)
def task_collect_all():
    """Coleta notícias para todos os políticos públicos."""
    from app.core.database import async_session_factory
    from app.models.politician import Politician
    from sqlalchemy import select

    async def _run():
        async with async_session_factory() as db:
            result = await db.execute(
                select(Politician.id).where(
                    Politician.is_public == True, Politician.deleted_at == None
                )
            )
            politician_ids = result.scalars().all()

        for pid in politician_ids:
            task_collect_for_politician.delay(str(pid))

        return {"dispatched": len(politician_ids)}

    return asyncio.run(_run())
