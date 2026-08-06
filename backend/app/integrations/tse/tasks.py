"""Celery tasks para integração TSE."""

import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="tse.import_candidates",
    bind=True,
    max_retries=2,
    default_retry_delay=120,
    time_limit=3600,
    soft_time_limit=3300,
)
def task_import_candidates(self, file_path: str, year: int, dataset_id: str | None = None):
    """Importa candidatos de arquivo CSV do TSE."""
    import uuid
    from app.core.database import async_session_factory
    from app.integrations.tse.services import TseImportService

    async def _run():
        async with async_session_factory() as db:
            service = TseImportService(db)
            ds_id = uuid.UUID(dataset_id) if dataset_id else None
            stats = await service.import_candidates_from_file(file_path, year, ds_id)
            await db.commit()
            return stats

    try:
        stats = asyncio.run(_run())
        logger.info("TSE candidates import completed: %s", stats)
        return stats
    except Exception as exc:
        logger.error("TSE candidates import failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(
    name="tse.download_dataset",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    time_limit=600,
    soft_time_limit=540,
)
def task_download_dataset(self, url: str, dest_path: str, expected_checksum: str | None = None):
    """Baixa dataset do TSE."""
    from app.integrations.tse.client import TseClient

    async def _run():
        client = TseClient()
        try:
            result = await client.download_file(url, dest_path, expected_checksum)
            return result
        finally:
            await client.close()

    try:
        result = asyncio.run(_run())
        logger.info("TSE dataset downloaded: %s", result)
        return result
    except Exception as exc:
        logger.error("TSE download failed: %s", exc)
        raise self.retry(exc=exc)
