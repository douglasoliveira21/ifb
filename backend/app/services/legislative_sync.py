"""Base service for legislative synchronization with job tracking."""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legislative import SyncCheckpoint
from app.models.sync import SyncJob

logger = logging.getLogger(__name__)


class LegislativeSyncService(ABC):
    """Base class for all legislative sync services."""

    provider: str = ""
    resource: str = ""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._job: SyncJob | None = None

    async def create_job(self, scope: str | None = None, requested_by: str | None = None) -> SyncJob:
        """Creates a sync job record."""
        job = SyncJob(
            provider=self.provider,
            resource=self.resource,
            scope=scope,
            status="running",
            requested_by=requested_by,
            started_at=datetime.now(UTC),
        )
        self.db.add(job)
        await self.db.flush()
        self._job = job
        return job

    async def complete_job(self, stats: dict) -> None:
        """Marks job as completed."""
        if self._job:
            self._job.status = "completed" if stats.get("error_records", 0) == 0 else "completed_with_errors"
            self._job.finished_at = datetime.now(UTC)
            self._job.total_records = stats.get("total", 0)
            self._job.processed_records = stats.get("processed", 0)
            self._job.created_records = stats.get("created", 0)
            self._job.updated_records = stats.get("updated", 0)
            self._job.duplicate_records = stats.get("duplicates", 0)
            self._job.error_records = stats.get("errors", 0)
            await self.db.flush()

    async def fail_job(self, error: str) -> None:
        """Marks job as failed."""
        if self._job:
            self._job.status = "failed"
            self._job.finished_at = datetime.now(UTC)
            self._job.error_message = error[:2000]
            await self.db.flush()

    async def get_checkpoint(self) -> SyncCheckpoint | None:
        """Gets sync checkpoint for this provider/resource."""
        result = await self.db.execute(
            select(SyncCheckpoint).where(
                SyncCheckpoint.provider == self.provider,
                SyncCheckpoint.resource == self.resource,
            )
        )
        return result.scalar_one_or_none()

    async def update_checkpoint(self, **kwargs) -> None:
        """Updates or creates sync checkpoint."""
        checkpoint = await self.get_checkpoint()
        if not checkpoint:
            checkpoint = SyncCheckpoint(
                provider=self.provider,
                resource=self.resource,
            )
            self.db.add(checkpoint)

        checkpoint.last_success_at = datetime.now(UTC)
        for key, value in kwargs.items():
            if hasattr(checkpoint, key):
                setattr(checkpoint, key, value)
        await self.db.flush()

    @abstractmethod
    async def fetch(self, **params) -> list[dict]:
        """Fetches raw data from external source."""
        ...

    @abstractmethod
    async def persist(self, items: list[dict]) -> dict:
        """Persists normalized data. Returns stats dict."""
        ...

    async def sync(self, scope: str | None = None, **params) -> dict:
        """Full sync flow: create job → fetch → persist → complete."""
        await self.create_job(scope=scope)
        try:
            raw_data = await self.fetch(**params)
            stats = await self.persist(raw_data)
            await self.complete_job(stats)
            await self.update_checkpoint()
            await self.db.commit()
            logger.info("[%s.%s] Sync completed: %s", self.provider, self.resource, stats)
            return stats
        except Exception as e:
            await self.fail_job(str(e))
            await self.db.commit()
            logger.error("[%s.%s] Sync failed: %s", self.provider, self.resource, e)
            raise
