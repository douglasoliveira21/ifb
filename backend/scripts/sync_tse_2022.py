"""
Importação TSE — Eleição 2022 (piloto)
Execute: python scripts/sync_tse_2022.py

Importa candidaturas, resultados, bens, receitas e despesas
usando a API DivulgaCandContas do TSE.
"""

import asyncio
import hashlib
import os
import sys
from datetime import UTC, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.politician import Politician
from app.models.election import (
    Election, Candidacy, CandidateAsset, CampaignRevenue, CampaignExpense, ElectionResult,
)

settings = get_settings()

# DivulgaCandContas API (public, no auth needed)
TSE_API = "https://divulgacandcontas.tse.jus.br/divulga/rest/v1"
YEAR = 2022
UF = "SP"  # São Paulo — well represented in our DB


async def get_or_create_election(db: AsyncSession) -> Election:
    """Get or create 2022 general election."""
    result = await db.execute(
        select(Election).where(Election.year == YEAR, Election.election_type == "general")
    )
    election = result.scalar_one_or_none()
    if not election:
        election = Election(
            year=YEAR, name="Eleições Gerais 2022",
            election_type="general", scope="general",
            first_round_date=datetime(2022, 10, 2),
            status="concluded", source_id="tse",
            source_url="https://divulgacandcontas.tse.jus.br",
        )
        db.add(election)
        await db.flush()
    return election


async def find_matching_politicians(db: AsyncSession, limit: int = 10):
    """Find politicians from SP that we can try to match with TSE candidates."""
    result = await db.execute(
        select(Politician).where(
            Politician.state_code == UF,
            Politician.is_public == True,
            Politician.deleted_at == None,
        ).limit(limit)
    )
    return result.scalars().all()


async def search_candidate_tse(client: httpx.AsyncClient, name: str, year: int = YEAR) -> dict | None:
    """Search TSE API for a candidate by name."""
    try:
        # Use the candidaturas endpoint
        resp = await client.get(
            f"{TSE_API}/candidatura/listar/{year}/SP/2045202022/candidatos",
            params={"nomeUrnaCandidato": name},
            headers={"Accept": "application/json"},
        )
        if resp.status_code == 200:
            dados = resp.json()
            candidatos = dados.get("candidatos", [])
            if candidatos:
                return candidatos[0]
    except Exception:
        pass

    # Try general federal election code
    try:
        resp = await client.get(
            f"{TSE_API}/candidatura/listar/{year}/SP/2040602022/candidatos",
            params={"nomeUrnaCandidato": name},
            headers={"Accept": "application/json"},
        )
        if resp.status_code == 200:
            dados = resp.json()
            candidatos = dados.get("candidatos", [])
            if candidatos:
                return candidatos[0]
    except Exception:
        pass

    return None


async def import_candidate_details(
    client: httpx.AsyncClient, db: AsyncSession, election: Election,
    politician: Politician, candidate_data: dict
):
    """Import full candidacy details: assets, revenues, expenses."""
    cand_id = candidate_data.get("id")
    sq = candidate_data.get("numero", "")
    nome_urna = candidate_data.get("nomeUrna", "")

    # Check if candidacy already exists
    existing = await db.execute(
        select(Candidacy).where(
            Candidacy.election_id == election.id,
            Candidacy.politician_id == politician.id,
        )
    )
    if existing.scalar_one_or_none():
        return {"skipped": True}

    stats = {"assets": 0, "revenues": 0, "expenses": 0}

    # Create candidacy
    candidacy = Candidacy(
        politician_id=politician.id,
        election_id=election.id,
        tse_candidate_id=str(cand_id) if cand_id else None,
        ballot_name=nome_urna or politician.full_name,
        full_name=candidate_data.get("nomeCompleto", politician.full_name),
        ballot_number=str(candidate_data.get("numero", "")),
        party_id=politician.current_party_id,
        state_code=UF,
        status=candidate_data.get("descricaoSituacao", "deferido"),
        reelection=candidate_data.get("reeleicao", False),
        source_id="tse",
        source_url=f"https://divulgacandcontas.tse.jus.br/divulga/#/candidato/{YEAR}/{cand_id}",
        collected_at=datetime.now(UTC),
        reconciliation_status="matched",
    )
    db.add(candidacy)
    await db.flush()

    # Import assets (bens)
    if cand_id:
        try:
            resp = await client.get(
                f"{TSE_API}/candidatura/buscar/{YEAR}/SP/{cand_id}/bens",
                headers={"Accept": "application/json"},
            )
            if resp.status_code == 200:
                bens = resp.json()
                if isinstance(bens, list):
                    for bem in bens:
                        valor = bem.get("valor", 0)
                        if isinstance(valor, str):
                            valor = float(valor.replace(",", ".").replace(".", "", valor.count(".") - 1)) if valor else 0

                        asset = CandidateAsset(
                            candidacy_id=candidacy.id,
                            category_name=bem.get("tipoBem", ""),
                            description=bem.get("descricao", "Não informado")[:2000],
                            declared_value=float(valor) if valor else 0,
                            source_id="tse",
                            collected_at=datetime.now(UTC),
                        )
                        db.add(asset)
                        stats["assets"] += 1
        except Exception as e:
            print(f"        Erro bens: {e}")

    # Import revenues (receitas)
    if cand_id:
        try:
            resp = await client.get(
                f"{TSE_API}/prestador/consulta/receitas/{YEAR}/{cand_id}",
                headers={"Accept": "application/json"},
            )
            if resp.status_code == 200:
                data = resp.json()
                receitas = data if isinstance(data, list) else data.get("receitas", data.get("data", []))
                if isinstance(receitas, list):
                    for rec in receitas[:50]:
                        valor = rec.get("valor", 0)
                        if isinstance(valor, str):
                            valor = float(valor.replace(",", ".")) if valor else 0

                        revenue = CampaignRevenue(
                            candidacy_id=candidacy.id,
                            donor_name=rec.get("nomeFornecedor", rec.get("nomeDoador")),
                            donor_type=rec.get("tipoFornecedor"),
                            revenue_type=rec.get("fonteRecurso", rec.get("tipoReceita")),
                            amount=float(valor) if valor else 0,
                            description=rec.get("descricao"),
                            source_id="tse",
                            collected_at=datetime.now(UTC),
                        )
                        db.add(revenue)
                        stats["revenues"] += 1
        except Exception as e:
            print(f"        Erro receitas: {e}")

    # Import expenses (despesas)
    if cand_id:
        try:
            resp = await client.get(
                f"{TSE_API}/prestador/consulta/despesas/{YEAR}/{cand_id}",
                headers={"Accept": "application/json"},
            )
            if resp.status_code == 200:
                data = resp.json()
                despesas = data if isinstance(data, list) else data.get("despesas", data.get("data", []))
                if isinstance(despesas, list):
                    for desp in despesas[:50]:
                        valor = desp.get("valor", 0)
                        if isinstance(valor, str):
                            valor = float(valor.replace(",", ".")) if valor else 0

                        expense = CampaignExpense(
                            candidacy_id=candidacy.id,
                            supplier_name=desp.get("nomeFornecedor"),
                            expense_type=desp.get("descricaoTipoDespesa", desp.get("tipoDocumento")),
                            amount=float(valor) if valor else 0,
                            description=desp.get("descricao"),
                            source_id="tse",
                            collected_at=datetime.now(UTC),
                        )
                        db.add(expense)
                        stats["expenses"] += 1
        except Exception as e:
            print(f"        Erro despesas: {e}")

    await db.flush()
    return stats


async def main():
    print("\n" + "=" * 60)
    print(f"  IMPORTAÇÃO TSE — Eleições {YEAR} ({UF})")
    print("=" * 60 + "\n")

    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(engine, class_=AsyncSession)

    async with factory() as db:
        election = await get_or_create_election(db)
        politicians = await find_matching_politicians(db, limit=10)

        print(f"  Eleição: {election.name}")
        print(f"  Políticos piloto: {len(politicians)} de {UF}")

        total = {"candidacies": 0, "assets": 0, "revenues": 0, "expenses": 0, "not_found": 0, "skipped": 0}

        async with httpx.AsyncClient(timeout=30) as client:
            for pol in politicians:
                print(f"\n  [{pol.full_name}]")

                # Try to find in TSE
                name_to_search = pol.ballot_name or pol.full_name
                candidate = await search_candidate_tse(client, name_to_search)

                if not candidate:
                    # Try just last name
                    parts = pol.full_name.split()
                    if len(parts) > 1:
                        candidate = await search_candidate_tse(client, parts[-1])

                if not candidate:
                    print(f"    ⚠ Não encontrado no TSE")
                    total["not_found"] += 1
                    continue

                print(f"    Encontrado: {candidate.get('nomeUrna', '')} (ID: {candidate.get('id', '')})")

                stats = await import_candidate_details(client, db, election, pol, candidate)
                if stats.get("skipped"):
                    print(f"    → Já importado")
                    total["skipped"] += 1
                else:
                    total["candidacies"] += 1
                    total["assets"] += stats.get("assets", 0)
                    total["revenues"] += stats.get("revenues", 0)
                    total["expenses"] += stats.get("expenses", 0)
                    print(f"    → Bens: {stats.get('assets', 0)}, Receitas: {stats.get('revenues', 0)}, Despesas: {stats.get('expenses', 0)}")

                await asyncio.sleep(1)  # Rate limit

        await db.commit()

    await engine.dispose()

    print("\n" + "=" * 60)
    print("  RESULTADO TSE")
    print("=" * 60)
    for k, v in total.items():
        print(f"  {k}: {v}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
