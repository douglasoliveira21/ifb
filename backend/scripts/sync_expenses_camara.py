"""
Importação de gastos parlamentares (CEAP) — Câmara dos Deputados.
Execute: python scripts/sync_expenses_camara.py [ano] [batch_size] [offset]

Exemplos:
  python scripts/sync_expenses_camara.py 2023
  python scripts/sync_expenses_camara.py 2024
  python scripts/sync_expenses_camara.py 2025
  python scripts/sync_expenses_camara.py 2023 50 0

Fonte: https://dadosabertos.camara.leg.br/api/v2/deputados/{id}/despesas
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
from app.models.politician import Politician, PoliticalPosition
from app.models.legislative import (
    LegislativeHouse, Legislator, ParliamentaryExpense, PoliticianLegislativeProfile,
)

settings = get_settings()
CAMARA_API = "https://dadosabertos.camara.leg.br/api/v2"

YEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
BATCH_SIZE = int(sys.argv[2]) if len(sys.argv) > 2 else 50
OFFSET = int(sys.argv[3]) if len(sys.argv) > 3 else 0


def extract_camara_id(source_url: str | None) -> str | None:
    if not source_url or "deputados/" not in str(source_url):
        return None
    parts = str(source_url).split("/")
    for i, p in enumerate(parts):
        if p == "deputados" and i + 1 < len(parts):
            return parts[i + 1]
    return None


async def main():
    print(f"\n{'=' * 60}")
    print(f"  GASTOS PARLAMENTARES — CÂMARA {YEAR}")
    print(f"  Batch={BATCH_SIZE}, Offset={OFFSET}")
    print(f"{'=' * 60}\n")

    engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=3)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

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
        print(f"  Total deputados: {total_in_db}")
        print(f"  Processando: {len(deputies)} (offset={OFFSET})\n")

        stats = {"expenses_created": 0, "duplicates": 0, "errors": 0, "deputies_processed": 0}

        async with httpx.AsyncClient(timeout=30, headers={"Accept": "application/json"}) as client:
            for i, dep in enumerate(deputies):
                camara_id = extract_camara_id(dep.source_url)
                if not camara_id:
                    continue

                try:
                    # Ensure legislator exists
                    leg_r = await db.execute(
                        select(Legislator).where(Legislator.external_id == camara_id, Legislator.house_id == house.id)
                    )
                    legislator = leg_r.scalar_one_or_none()
                    if not legislator:
                        legislator = Legislator(
                            house_id=house.id, external_id=camara_id,
                            full_name=dep.full_name, state_code=dep.state_code,
                            status="active", last_synced_at=datetime.now(UTC),
                        )
                        db.add(legislator)
                        await db.flush()

                    # Fetch expenses
                    page = 1
                    while True:
                        resp = await client.get(
                            f"{CAMARA_API}/deputados/{camara_id}/despesas",
                            params={"ano": str(YEAR), "itens": "75", "pagina": str(page), "ordem": "ASC", "ordenarPor": "mes"},
                        )
                        if resp.status_code != 200:
                            break

                        items = resp.json().get("dados", [])
                        if not items:
                            break

                        for item in items:
                            # Build external_id for deduplication
                            doc_num = item.get("numDocumento", "")
                            ext_id = f"{camara_id}-{YEAR}-{item.get('mes', 0)}-{doc_num}"

                            # Check duplicate
                            existing = await db.execute(
                                select(ParliamentaryExpense.id).where(
                                    ParliamentaryExpense.external_id == ext_id
                                )
                            )
                            if existing.scalar_one_or_none():
                                stats["duplicates"] += 1
                                continue

                            net = item.get("valorLiquido", 0) or 0
                            gross = item.get("valorDocumento", 0) or 0

                            db.add(ParliamentaryExpense(
                                house_id=house.id,
                                legislator_id=legislator.id,
                                external_id=ext_id,
                                year=YEAR,
                                month=item.get("mes", 0),
                                category=(item.get("tipoDespesa") or "Outros")[:255],
                                supplier_name=(item.get("nomeFornecedor") or "")[:500] or None,
                                supplier_document_hash=hashlib.md5((item.get("cnpjCpfFornecedor") or "").encode()).hexdigest() if item.get("cnpjCpfFornecedor") else None,
                                document_number=str(doc_num)[:100] if doc_num else None,
                                gross_amount=float(gross),
                                net_amount=float(net),
                                reimbursement_amount=float(item.get("valorGlosa", 0) or 0),
                                document_url=item.get("urlDocumento"),
                                source_url=f"{CAMARA_API}/deputados/{camara_id}/despesas",
                            ))
                            stats["expenses_created"] += 1

                        if len(items) < 75:
                            break
                        page += 1
                        await asyncio.sleep(0.2)

                    stats["deputies_processed"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    if stats["errors"] <= 5:
                        print(f"  Erro {dep.full_name}: {e}")

                if (i + 1) % 10 == 0:
                    await db.flush()
                    print(f"  ... {i+1}/{len(deputies)} | despesas={stats['expenses_created']} dupes={stats['duplicates']} erros={stats['errors']}")

                await asyncio.sleep(0.3)

        await db.commit()

    await engine.dispose()

    print(f"\n{'=' * 60}")
    print(f"  RESULTADO — GASTOS {YEAR}")
    print(f"{'=' * 60}")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"\n  Próximo: python scripts/sync_expenses_camara.py {YEAR} {BATCH_SIZE} {OFFSET + BATCH_SIZE}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
