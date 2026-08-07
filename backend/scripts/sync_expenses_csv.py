"""
Importação de gastos parlamentares via CSV — Dados Abertos da Câmara.
Execute: python scripts/sync_expenses_csv.py [ano]

Exemplos:
  python scripts/sync_expenses_csv.py 2023
  python scripts/sync_expenses_csv.py 2024
  python scripts/sync_expenses_csv.py 2025

Fonte: https://dadosabertos.camara.leg.br/arquivos/despesas/csv/Ano-{ano}.csv
"""

import asyncio
import csv
import hashlib
import io
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
CSV_URL = f"https://www.camara.leg.br/cotas/Ano-{YEAR}.csv.zip"


async def main():
    print(f"\n{'=' * 60}")
    print(f"  GASTOS PARLAMENTARES VIA CSV — {YEAR}")
    print(f"  Fonte: {CSV_URL}")
    print(f"{'=' * 60}\n")

    # Download CSV (ZIP)
    print("  Baixando ZIP...")
    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
        resp = await client.get(CSV_URL)
        if resp.status_code != 200:
            print(f"  Erro ao baixar: {resp.status_code}")
            print(f"  URL: {CSV_URL}")
            return
        zip_data = resp.content

    print(f"  ZIP baixado: {len(zip_data)} bytes")

    # Extract CSV from ZIP
    import zipfile
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
        csv_filename = [n for n in zf.namelist() if n.endswith(".csv")][0]
        print(f"  Extraindo: {csv_filename}")
        csv_text = zf.read(csv_filename).decode("utf-8", errors="replace")

    print(f"  CSV extraído: {len(csv_text)} caracteres")

    # Parse CSV
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")
    rows = list(reader)
    print(f"  Linhas no CSV: {len(rows)}")

    if not rows:
        print("  CSV vazio!")
        return

    # Show column names for debug
    print(f"  Colunas: {list(rows[0].keys())[:10]}")

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

        # Build legislator cache by external_id
        leg_r = await db.execute(select(Legislator).where(Legislator.house_id == house.id))
        legislators = {leg.external_id: leg for leg in leg_r.scalars().all()}
        print(f"  Legisladores no banco: {len(legislators)}")

        stats = {"created": 0, "duplicates": 0, "no_legislator": 0, "errors": 0}

        for i, row in enumerate(rows):
            try:
                # CSV columns (may vary, common names):
                dep_id = str(row.get("idDeputado") or row.get("nuDeputadoId") or row.get("txNomeParlamentar", "")).strip()

                # Try to find by idDeputado
                if not dep_id or not dep_id.isdigit():
                    # Try to match by name
                    stats["no_legislator"] += 1
                    continue

                legislator = legislators.get(dep_id)
                if not legislator:
                    # Create legislator
                    nome = row.get("txNomeParlamentar") or row.get("nomeParlamentar") or ""
                    sg_uf = row.get("sgUF") or row.get("siglaUF") or ""
                    sg_partido = row.get("sgPartido") or row.get("siglaPartido") or ""
                    
                    legislator = Legislator(
                        house_id=house.id, external_id=dep_id,
                        full_name=nome, state_code=sg_uf,
                        party_acronym=sg_partido,
                        status="active", last_synced_at=datetime.now(UTC),
                    )
                    db.add(legislator)
                    await db.flush()
                    legislators[dep_id] = legislator

                # Parse expense data
                mes = int(row.get("numMes") or row.get("mes") or row.get("nummes") or 0)
                doc_num = row.get("txtNumero") or row.get("numDocumento") or row.get("numRessarcimento") or ""
                categoria = row.get("txtDescricao") or row.get("tipoDespesa") or row.get("txtdescricao") or "Outros"
                fornecedor = row.get("txtFornecedor") or row.get("nomeFornecedor") or ""
                cnpj = row.get("txtCNPJCPF") or row.get("cnpjCpfFornecedor") or ""

                # Parse amounts (Brazilian format: 1.234,56)
                def parse_br_number(val):
                    if not val:
                        return 0.0
                    val = str(val).strip()
                    if not val or val == "":
                        return 0.0
                    # Handle Brazilian format
                    val = val.replace(".", "").replace(",", ".")
                    try:
                        return float(val)
                    except ValueError:
                        return 0.0

                valor_doc = parse_br_number(row.get("vlrDocumento") or row.get("valorDocumento"))
                valor_liq = parse_br_number(row.get("vlrLiquido") or row.get("valorLiquido"))
                valor_glosa = parse_br_number(row.get("vlrGlosa") or row.get("valorGlosa"))

                # External ID for deduplication
                ext_id = f"{dep_id}-{YEAR}-{mes}-{doc_num}"

                # Check duplicate
                existing = await db.execute(
                    select(ParliamentaryExpense.id).where(ParliamentaryExpense.external_id == ext_id)
                )
                if existing.scalar_one_or_none():
                    stats["duplicates"] += 1
                    continue

                db.add(ParliamentaryExpense(
                    house_id=house.id,
                    legislator_id=legislator.id,
                    external_id=ext_id,
                    year=YEAR,
                    month=mes,
                    category=categoria[:255],
                    supplier_name=fornecedor[:500] if fornecedor else None,
                    supplier_document_hash=hashlib.md5(cnpj.encode()).hexdigest() if cnpj else None,
                    document_number=str(doc_num)[:100] if doc_num else None,
                    gross_amount=valor_doc,
                    net_amount=valor_liq,
                    reimbursement_amount=valor_glosa,
                    source_url=CSV_URL,
                ))
                stats["created"] += 1

            except Exception as e:
                stats["errors"] += 1
                if stats["errors"] <= 5:
                    print(f"  Erro linha {i}: {e}")
                    print(f"  Row: {dict(list(row.items())[:5])}")

            if (i + 1) % 5000 == 0:
                await db.flush()
                print(f"  ... {i+1}/{len(rows)} | criadas={stats['created']} dupes={stats['duplicates']} erros={stats['errors']}")

        await db.commit()

    await engine.dispose()

    print(f"\n{'=' * 60}")
    print(f"  RESULTADO — GASTOS {YEAR} (CSV)")
    print(f"{'=' * 60}")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
