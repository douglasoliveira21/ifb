"""Celery tasks para sincronização com o Senado Federal."""

import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="senado.sync_senators",
    bind=True,
    max_retries=2,
    time_limit=1800,
    soft_time_limit=1700,
)
def task_sync_senators(self):
    """Sincroniza lista de senadores em exercício."""
    from app.core.database import async_session_factory
    from app.integrations.senado.client import SenadoClient
    from app.models.legislative import Legislator, LegislativeHouse
    from sqlalchemy import select

    async def _run():
        client = SenadoClient()
        try:
            senators = await client.list_current_senators()
            async with async_session_factory() as db:
                house_result = await db.execute(
                    select(LegislativeHouse).where(LegislativeHouse.acronym == "SF")
                )
                house = house_result.scalar_one_or_none()
                if not house:
                    house = LegislativeHouse(
                        name="Senado Federal", acronym="SF",
                        api_base_url="https://legis.senado.leg.br/dadosabertos",
                    )
                    db.add(house)
                    await db.flush()

                created = 0
                updated = 0
                for sen in senators:
                    ident = sen.get("IdentificacaoParlamentar", {})
                    ext_id = str(ident.get("CodigoParlamentar", ""))
                    if not ext_id:
                        continue

                    existing = await db.execute(
                        select(Legislator).where(
                            Legislator.house_id == house.id,
                            Legislator.external_id == ext_id,
                        )
                    )
                    legislator = existing.scalar_one_or_none()
                    name = ident.get("NomeParlamentar", "")
                    party = ident.get("SiglaPartidoParlamentar")
                    uf = ident.get("UfParlamentar")
                    photo = ident.get("UrlFotoParlamentar")

                    if legislator:
                        legislator.full_name = name
                        legislator.party_acronym = party
                        legislator.state_code = uf
                        legislator.photo_url = photo
                        updated += 1
                    else:
                        legislator = Legislator(
                            house_id=house.id,
                            external_id=ext_id,
                            full_name=name,
                            party_acronym=party,
                            state_code=uf,
                            photo_url=photo,
                            status="active",
                        )
                        db.add(legislator)
                        created += 1

                await db.commit()
                return {"created": created, "updated": updated, "total": len(senators)}
        finally:
            await client.close()

    try:
        result = asyncio.run(_run())
        logger.info("Senado senators sync: %s", result)
        return result
    except Exception as exc:
        logger.error("Senado senators sync failed: %s", exc)
        raise self.retry(exc=exc)
