"""
Expansão: Proposições e Comissões para TODOS os deputados.
Execute: python scripts/expand_all_deputies.py [batch_size] [offset]

Exemplo: python scripts/expand_all_deputies.py 50 0
         python scripts/expand_all_deputies.py 50 50
"""

import asyncio
import os
import sys
from datetime import UTC, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.politician import Politician, PoliticalPosition
from app.models.legislative import (
    LegislativeHouse, Legislator, PoliticianLegislativeProfile,
    LegislativeProposition, PropositionAuthor,
    LegislativeCommittee, CommitteeMembership,
)

settings = get_settings()
CAMARA_API = "https://dadosabertos.camara.leg.br/api/v2"

BATCH_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 50
OFFSET = int(sys.argv[2]) if len(sys.argv) > 2 else 0


async def get_camara_id(politician: Politician) -> str | None:
    if politician.source_url and "deputados/" in str(politician.source_url):
        parts = str(politician.source_url).split("/")
        for i, p in enumerate(parts):
            if p == "deputados" and i + 1 < len(parts):
                return parts[i + 1]
    return None


async def main():
    print(f"\n=== EXPANSÃO DEPUTADOS (batch={BATCH_SIZE}, offset={OFFSET}) ===\n")

    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(engine, class_=AsyncSession)

    async with factory() as db:
        # Get house
        house_r = await db.execute(select(LegislativeHouse).where(LegislativeHouse.acronym == "CD"))
        house = house_r.scalar_one_or_none()
        if not house:
            house = LegislativeHouse(name="Câmara dos Deputados", acronym="CD", api_base_url=CAMARA_API)
            db.add(house)
            await db.flush()

        # Get deputies
        pos_r = await db.execute(select(PoliticalPosition.id).where(PoliticalPosition.name == "Deputado Federal"))
        pos_id = pos_r.scalar_one_or_none()

        deps_r = await db.execute(
            select(Politician).where(
                Politician.current_position_id == pos_id,
                Politician.is_public == True,
                Politician.source_url != None,
            ).order_by(Politician.full_name).offset(OFFSET).limit(BATCH_SIZE)
        )
        deputies = deps_r.scalars().all()

        total_count_r = await db.execute(
            select(func.count(Politician.id)).where(
                Politician.current_position_id == pos_id, Politician.is_public == True,
            )
        )
        total_in_db = total_count_r.scalar_one()

        print(f"  Total deputados no banco: {total_in_db}")
        print(f"  Processando: {len(deputies)} (offset={OFFSET})")

        stats = {"propositions": 0, "committees": 0, "errors": 0, "skipped": 0}

        async with httpx.AsyncClient(timeout=30, headers={"Accept": "application/json"}) as client:
            for i, dep in enumerate(deputies):
                camara_id = await get_camara_id(dep)
                if not camara_id:
                    stats["skipped"] += 1
                    continue

                try:
                    # Propositions
                    resp = await client.get(f"{CAMARA_API}/proposicoes",
                                           params={"idDeputadoAutor": camara_id, "itens": 30, "ordem": "DESC", "ordenarPor": "id"})
                    if resp.status_code == 200:
                        props = resp.json().get("dados", [])
                        for p in props:
                            ext_id = str(p.get("id", ""))
                            existing = await db.execute(
                                select(LegislativeProposition.id).where(
                                    LegislativeProposition.external_id == ext_id,
                                    LegislativeProposition.house_id == house.id,
                                )
                            )
                            if not existing.scalar_one_or_none():
                                prop = LegislativeProposition(
                                    house_id=house.id, external_id=ext_id,
                                    type_acronym=p.get("siglaTipo", ""),
                                    number=p.get("numero"), year=p.get("ano"),
                                    title=(p.get("ementa") or "")[:1000],
                                    source_url=p.get("uri"),
                                    last_synced_at=datetime.now(UTC),
                                )
                                db.add(prop)
                                await db.flush()
                                db.add(PropositionAuthor(
                                    proposition_id=prop.id, author_name=dep.full_name,
                                    author_type="legislator", is_primary=True,
                                ))
                                stats["propositions"] += 1

                    # Committees
                    resp2 = await client.get(f"{CAMARA_API}/deputados/{camara_id}/orgaos", params={"itens": 30})
                    if resp2.status_code == 200:
                        # Ensure legislator exists
                        leg_r = await db.execute(
                            select(Legislator).where(Legislator.external_id == camara_id, Legislator.house_id == house.id)
                        )
                        legislator = leg_r.scalar_one_or_none()
                        if not legislator:
                            legislator = Legislator(house_id=house.id, external_id=camara_id,
                                                   full_name=dep.full_name, state_code=dep.state_code,
                                                   status="active", last_synced_at=datetime.now(UTC))
                            db.add(legislator)
                            await db.flush()
                            # Link profile
                            db.add(PoliticianLegislativeProfile(
                                politician_id=dep.id, legislator_id=legislator.id,
                                house_id=house.id, match_method="source_url",
                                match_confidence=100.0, status="confirmed",
                            ))
                            await db.flush()

                        organs = resp2.json().get("dados", [])
                        for org in organs:
                            ext_id = str(org.get("idOrgao", ""))
                            if not ext_id:
                                continue
                            com_r = await db.execute(
                                select(LegislativeCommittee).where(
                                    LegislativeCommittee.external_id == ext_id,
                                    LegislativeCommittee.house_id == house.id,
                                )
                            )
                            committee = com_r.scalar_one_or_none()
                            if not committee:
                                committee = LegislativeCommittee(
                                    house_id=house.id, external_id=ext_id,
                                    name=(org.get("nomeOrgao") or "")[:500],
                                    acronym=org.get("siglaOrgao"),
                                    committee_type=org.get("tipoOrgao"),
                                )
                                db.add(committee)
                                await db.flush()

                            mem_r = await db.execute(
                                select(CommitteeMembership.id).where(
                                    CommitteeMembership.committee_id == committee.id,
                                    CommitteeMembership.legislator_id == legislator.id,
                                )
                            )
                            if not mem_r.scalar_one_or_none():
                                db.add(CommitteeMembership(
                                    committee_id=committee.id, legislator_id=legislator.id,
                                    role=org.get("titulo", "Membro") or "Membro",
                                ))
                                stats["committees"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    if stats["errors"] <= 5:
                        print(f"    Erro {dep.full_name}: {e}")

                # Flush and report every 10
                if (i + 1) % 10 == 0:
                    await db.flush()
                    print(f"  ... {i + 1}/{len(deputies)} | props={stats['propositions']} comms={stats['committees']} errs={stats['errors']}")

                await asyncio.sleep(0.5)  # Rate limit

        await db.commit()

    await engine.dispose()

    print(f"\n=== RESULTADO ===")
    print(f"  Proposições: {stats['propositions']}")
    print(f"  Comissões: {stats['committees']}")
    print(f"  Erros: {stats['errors']}")
    print(f"  Pulados (sem ID): {stats['skipped']}")
    print(f"\n  Próximo: python scripts/expand_all_deputies.py {BATCH_SIZE} {OFFSET + BATCH_SIZE}\n")


if __name__ == "__main__":
    asyncio.run(main())
