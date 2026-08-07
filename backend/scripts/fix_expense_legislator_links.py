"""
Corrige vínculo de despesas: busca o nome do deputado no CSV original e vincula
ao legislador correto (o que está no PoliticianLegislativeProfile).

Execute: python scripts/fix_expense_legislator_links.py

O problema: CSV criou legisladores sem nome usando ideCadastro.
A solução: baixa o CSV novamente, mapeia ideCadastro → nome, e reasigna despesas.
"""

import asyncio
import csv
import io
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.politician import Politician, PoliticalPosition
from app.models.legislative import (
    Legislator, LegislativeHouse, ParliamentaryExpense, PoliticianLegislativeProfile,
)

settings = get_settings()


async def main():
    print(f"\n{'=' * 60}")
    print(f"  CORRIGINDO VÍNCULO DE DESPESAS")
    print(f"{'=' * 60}\n")

    # 1. Download CSVs to get ideCadastro → nome mapping (need 2023+2024 for older IDs)
    id_to_name: dict[str, str] = {}

    for year in [2024, 2023, 2025]:
        print(f"  Baixando CSV {year} para mapeamento...")
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            resp = await client.get(f"https://www.camara.leg.br/cotas/Ano-{year}.csv.zip")
            if resp.status_code != 200:
                print(f"  Erro download {year}: {resp.status_code}")
                continue

        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            csv_file = [n for n in zf.namelist() if n.endswith(".csv")][0]
            csv_text = zf.read(csv_file).decode("utf-8", errors="replace")

        reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")
        count_before = len(id_to_name)
        for row in reader:
            ide = str(row.get("ideCadastro") or "").strip()
            nome = ""
            for k, v in row.items():
                if "nomeparlamentar" in k.lower().replace('"', ''):
                    nome = (v or "").strip()
                    break
            if ide and nome and ide not in id_to_name:
                id_to_name[ide] = nome
        print(f"  {year}: +{len(id_to_name) - count_before} novos (total: {len(id_to_name)})")

    print(f"  Mapeamento final: {len(id_to_name)} deputados (ideCadastro → nome)")

    # 2. Connect to DB and fix
    engine = create_async_engine(settings.database_url, pool_size=3, max_overflow=0)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as db:
        house_r = await db.execute(select(LegislativeHouse).where(LegislativeHouse.acronym == "CD"))
        house = house_r.scalar_one_or_none()

        # Get politicians by name (lowercase) → their linked legislator
        pos_r = await db.execute(select(PoliticalPosition.id).where(PoliticalPosition.name == "Deputado Federal"))
        pos_id = pos_r.scalar_one_or_none()

        profiles_r = await db.execute(
            select(PoliticianLegislativeProfile.legislator_id, Politician.full_name)
            .join(Politician, PoliticianLegislativeProfile.politician_id == Politician.id)
            .where(PoliticianLegislativeProfile.house_id == house.id)
        )
        name_to_leg_id: dict[str, any] = {}
        for leg_id, name in profiles_r.all():
            name_to_leg_id[name.strip().lower()] = leg_id

        print(f"  Políticos com perfil legislativo: {len(name_to_leg_id)}")

        # Get orphan legislators (have expenses, no profile)
        linked_ids = set(name_to_leg_id.values())
        orphans_r = await db.execute(
            select(Legislator.id, Legislator.external_id)
            .join(ParliamentaryExpense, ParliamentaryExpense.legislator_id == Legislator.id)
            .where(Legislator.house_id == house.id, Legislator.id.notin_(linked_ids))
            .group_by(Legislator.id)
        )
        orphans = orphans_r.all()
        print(f"  Legisladores órfãos com despesas: {len(orphans)}")

        stats = {"reassigned": 0, "no_match": 0}

        for orphan_id, orphan_ext_id in orphans:
            # Find name from CSV mapping
            nome = id_to_name.get(orphan_ext_id, "")
            if not nome:
                stats["no_match"] += 1
                continue

            # Find target legislator by politician name
            target_leg_id = name_to_leg_id.get(nome.strip().lower())
            if not target_leg_id:
                stats["no_match"] += 1
                continue

            # Reassign expenses
            result = await db.execute(
                update(ParliamentaryExpense)
                .where(ParliamentaryExpense.legislator_id == orphan_id)
                .values(legislator_id=target_leg_id)
            )
            stats["reassigned"] += result.rowcount

            if stats["reassigned"] % 10000 == 0 and stats["reassigned"] > 0:
                await db.flush()
                print(f"  ... reasignadas: {stats['reassigned']}")

        await db.commit()

    await engine.dispose()

    print(f"\n{'=' * 60}")
    print(f"  RESULTADO")
    print(f"{'=' * 60}")
    print(f"  Despesas reasignadas: {stats['reassigned']}")
    print(f"  Sem correspondência: {stats['no_match']}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
