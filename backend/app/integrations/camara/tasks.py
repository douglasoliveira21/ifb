"""Celery tasks para sincronização com a Câmara dos Deputados."""

import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="camara.sync_deputies",
    bind=True,
    max_retries=2,
    time_limit=1800,
    soft_time_limit=1700,
)
def task_sync_deputies(self, legislature: int | None = None):
    """Sincroniza lista de deputados da legislatura atual."""
    from app.core.database import async_session_factory
    from app.integrations.camara.client import CamaraClient
    from app.models.legislative import Legislator, LegislativeHouse
    from sqlalchemy import select

    async def _run():
        client = CamaraClient()
        try:
            deputies = await client.list_deputies(legislature=legislature)
            async with async_session_factory() as db:
                # Get or create house
                house_result = await db.execute(
                    select(LegislativeHouse).where(LegislativeHouse.acronym == "CD")
                )
                house = house_result.scalar_one_or_none()
                if not house:
                    house = LegislativeHouse(
                        name="Câmara dos Deputados", acronym="CD",
                        api_base_url="https://dadosabertos.camara.leg.br/api/v2",
                    )
                    db.add(house)
                    await db.flush()

                created = 0
                updated = 0
                for dep in deputies:
                    ext_id = str(dep.get("id", ""))
                    existing = await db.execute(
                        select(Legislator).where(
                            Legislator.house_id == house.id,
                            Legislator.external_id == ext_id,
                        )
                    )
                    legislator = existing.scalar_one_or_none()
                    if legislator:
                        legislator.full_name = dep.get("nome", "")
                        legislator.party_acronym = dep.get("siglaPartido")
                        legislator.state_code = dep.get("siglaUf")
                        legislator.photo_url = dep.get("urlFoto")
                        updated += 1
                    else:
                        legislator = Legislator(
                            house_id=house.id,
                            external_id=ext_id,
                            full_name=dep.get("nome", ""),
                            party_acronym=dep.get("siglaPartido"),
                            state_code=dep.get("siglaUf"),
                            photo_url=dep.get("urlFoto"),
                            status="active",
                        )
                        db.add(legislator)
                        created += 1

                await db.commit()
                return {"created": created, "updated": updated, "total": len(deputies)}
        finally:
            await client.close()

    try:
        result = asyncio.run(_run())
        logger.info("Câmara deputies sync: %s", result)
        return result
    except Exception as exc:
        logger.error("Câmara deputies sync failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(
    name="camara.sync_expenses",
    bind=True,
    max_retries=2,
    time_limit=3600,
    soft_time_limit=3500,
)
def task_sync_expenses(self, deputy_external_id: str | None = None, year: int | None = None):
    """Sincroniza despesas parlamentares (CEAP)."""
    logger.info("Câmara expenses sync started (deputy=%s, year=%s)", deputy_external_id, year)
    # Implementation will iterate over deputies and fetch expenses
    # Placeholder for the task signature
    return {"status": "pending_implementation"}


@celery_app.task(
    name="camara.sync_propositions",
    bind=True,
    max_retries=2,
    time_limit=1800,
)
def task_sync_propositions(self, year: int | None = None):
    """Sincroniza proposições recentes."""
    logger.info("Câmara propositions sync started (year=%s)", year)
    return {"status": "pending_implementation"}
