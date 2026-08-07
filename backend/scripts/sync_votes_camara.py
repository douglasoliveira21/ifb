"""
Sincronização de votações nominais da Câmara — Mandato atual (Legislatura 57)
Execute: python scripts/sync_votes_camara.py [--start-date 2023-02-01] [--end-date 2026-12-31]

Importa TODAS as votações nominais do período e vincula o voto de cada deputado
ao seu perfil no banco. Idempotente: não cria duplicatas.

Fonte: https://dadosabertos.camara.leg.br/api/v2/votacoes
"""

import asyncio
import os
import sys
from datetime import UTC, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.legislative import (
    Legislator,
    LegislativeHouse,
    LegislativeVoteEvent,
    LegislatorVote,
    PoliticianLegislativeProfile,
)
from app.models.politician import Politician, PoliticalPosition

settings = get_settings()
CAMARA_API = "https://dadosabertos.camara.leg.br/api/v2"

# Mandato atual: Legislatura 57 (2023-02-01 a 2027-01-31)
DEFAULT_START = "2023-02-01"
DEFAULT_END = datetime.now(UTC).strftime("%Y-%m-%d")  # Today (API rejects future dates)

# Parse CLI args
START_DATE = DEFAULT_START
END_DATE = DEFAULT_END
for i, arg in enumerate(sys.argv):
    if arg == "--start-date" and i + 1 < len(sys.argv):
        START_DATE = sys.argv[i + 1]
    if arg == "--end-date" and i + 1 < len(sys.argv):
        END_DATE = sys.argv[i + 1]

VOTE_MAP = {
    "Sim": "yes",
    "Não": "no",
    "Abstenção": "abstention",
    "Obstrução": "obstruction",
    "Art. 17": "art17",
    "Presidente": "president",
    "-": "absent",
    "Ausente": "absent",
}


async def get_or_create_house(db: AsyncSession) -> LegislativeHouse:
    result = await db.execute(select(LegislativeHouse).where(LegislativeHouse.acronym == "CD"))
    house = result.scalar_one_or_none()
    if not house:
        house = LegislativeHouse(name="Câmara dos Deputados", acronym="CD", api_base_url=CAMARA_API)
        db.add(house)
        await db.flush()
    return house


async def ensure_legislator(db: AsyncSession, house_id, dep_data: dict) -> Legislator | None:
    """Garante que o deputado existe como Legislator no banco."""
    ext_id = str(dep_data.get("id", ""))
    if not ext_id:
        return None

    result = await db.execute(
        select(Legislator).where(Legislator.external_id == ext_id, Legislator.house_id == house_id)
    )
    legislator = result.scalar_one_or_none()
    if legislator:
        return legislator

    # Criar legislator
    legislator = Legislator(
        house_id=house_id,
        external_id=ext_id,
        full_name=dep_data.get("nome", ""),
        party_acronym=dep_data.get("siglaPartido"),
        state_code=dep_data.get("siglaUf"),
        status="active",
        last_synced_at=datetime.now(UTC),
    )
    db.add(legislator)
    await db.flush()

    # Tentar vincular ao politician existente
    name = dep_data.get("nome", "")
    source_url = f"{CAMARA_API}/deputados/{ext_id}"
    pol_result = await db.execute(
        select(Politician).where(Politician.source_url.contains(ext_id))
    )
    politician = pol_result.scalar_one_or_none()
    if politician:
        # Verificar se já existe o link
        link_result = await db.execute(
            select(PoliticianLegislativeProfile).where(
                PoliticianLegislativeProfile.politician_id == politician.id,
                PoliticianLegislativeProfile.legislator_id == legislator.id,
            )
        )
        if not link_result.scalar_one_or_none():
            db.add(PoliticianLegislativeProfile(
                politician_id=politician.id,
                legislator_id=legislator.id,
                house_id=house_id,
                match_method="external_id",
                match_confidence=100.0,
                status="confirmed",
            ))
            await db.flush()

    return legislator


async def fetch_all_votacoes(client: httpx.AsyncClient, start: str, end: str) -> list[dict]:
    """Busca todas as votações nominais no período usando paginação."""
    all_votes = []
    page = 1
    items_per_page = 100

    while True:
        params = {
            "dataInicio": start,
            "dataFim": end,
            "ordem": "ASC",
            "ordenarPor": "dataHoraRegistro",
            "itens": str(items_per_page),
            "pagina": str(page),
        }
        resp = await client.get(f"{CAMARA_API}/votacoes", params=params)

        if resp.status_code != 200:
            print(f"  Erro página {page}: {resp.status_code}")
            try:
                print(f"  Resposta: {resp.text[:300]}")
            except Exception:
                pass
            break

        data = resp.json().get("dados", [])
        if not data:
            break

        all_votes.extend(data)
        print(f"  Página {page}: {len(data)} votações (total acumulado: {len(all_votes)})")

        if len(data) < items_per_page:
            break
        page += 1
        await asyncio.sleep(0.5)

    return all_votes


async def sync_vote_event(
    db: AsyncSession, client: httpx.AsyncClient, house: LegislativeHouse, votacao: dict
) -> dict:
    """Sincroniza uma votação e todos os votos individuais."""
    ext_id = str(votacao.get("id", ""))
    stats = {"created_event": False, "votes_created": 0, "votes_skipped": 0}

    if not ext_id:
        return stats

    # Check if event already exists
    existing = await db.execute(
        select(LegislativeVoteEvent).where(
            LegislativeVoteEvent.external_id == ext_id,
            LegislativeVoteEvent.house_id == house.id,
        )
    )
    event = existing.scalar_one_or_none()

    if not event:
        date_raw = votacao.get("dataHoraRegistro") or votacao.get("data")
        date_parsed = None
        if date_raw:
            try:
                date_parsed = datetime.fromisoformat(date_raw.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        event = LegislativeVoteEvent(
            house_id=house.id,
            external_id=ext_id,
            date=date_parsed,
            description=(votacao.get("descricao") or "")[:1000] or None,
            result=str(votacao.get("aprovacao", "")) if votacao.get("aprovacao") is not None else None,
            is_nominal=True,
            source_url=f"{CAMARA_API}/votacoes/{ext_id}",
        )
        db.add(event)
        await db.flush()
        stats["created_event"] = True

    # Fetch individual votes
    await asyncio.sleep(0.4)
    resp = await client.get(f"{CAMARA_API}/votacoes/{ext_id}/votos")
    if resp.status_code != 200:
        return stats

    votos = resp.json().get("dados", [])

    for voto in votos:
        dep = voto.get("deputado_", {})
        dep_id = str(dep.get("id", ""))
        if not dep_id:
            continue

        # Get or create legislator
        legislator = await ensure_legislator(db, house.id, {
            "id": dep_id,
            "nome": dep.get("nome", ""),
            "siglaPartido": dep.get("siglaPartido"),
            "siglaUf": dep.get("siglaUf"),
        })
        if not legislator:
            continue

        # Check if vote already exists
        vote_exists = await db.execute(
            select(LegislatorVote.vote_event_id).where(
                LegislatorVote.vote_event_id == event.id,
                LegislatorVote.legislator_id == legislator.id,
            )
        )
        if vote_exists.scalar_one_or_none():
            stats["votes_skipped"] += 1
            continue

        original = voto.get("tipoVoto", "Ausente")
        normalized = VOTE_MAP.get(original, "other")

        db.add(LegislatorVote(
            vote_event_id=event.id,
            legislator_id=legislator.id,
            original_vote=original,
            normalized_vote=normalized,
            party_at_vote=dep.get("siglaPartido"),
            state_at_vote=dep.get("siglaUf"),
        ))
        stats["votes_created"] += 1

    return stats


async def main():
    print(f"\n{'=' * 60}")
    print(f"  SINCRONIZAÇÃO DE VOTAÇÕES — CÂMARA DOS DEPUTADOS")
    print(f"  Período: {START_DATE} a {END_DATE}")
    print(f"{'=' * 60}\n")

    engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=3)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as db:
        house = await get_or_create_house(db)

        async with httpx.AsyncClient(timeout=30, headers={"Accept": "application/json"}) as client:
            # Split into 3-month chunks to avoid API limits
            from datetime import date, timedelta
            start_d = date.fromisoformat(START_DATE)
            end_d = date.fromisoformat(END_DATE)

            all_votacoes: list[dict] = []
            chunk_start = start_d
            while chunk_start < end_d:
                chunk_end = min(chunk_start + timedelta(days=90), end_d)
                print(f"  Buscando: {chunk_start} a {chunk_end}...")
                chunk = await fetch_all_votacoes(client, str(chunk_start), str(chunk_end))
                all_votacoes.extend(chunk)
                chunk_start = chunk_end + timedelta(days=1)
                await asyncio.sleep(0.5)

            print(f"\n  Total de votações encontradas: {len(all_votacoes)}\n")

            if not all_votacoes:
                print("  Nenhuma votação encontrada no período.")
                await engine.dispose()
                return

            # 2. Process each vote event
            print("  Processando votos individuais...")
            totals = {"events_created": 0, "votes_created": 0, "votes_skipped": 0, "errors": 0}

            for i, votacao in enumerate(all_votacoes):
                try:
                    stats = await sync_vote_event(db, client, house, votacao)
                    if stats["created_event"]:
                        totals["events_created"] += 1
                    totals["votes_created"] += stats["votes_created"]
                    totals["votes_skipped"] += stats["votes_skipped"]
                except Exception as e:
                    totals["errors"] += 1
                    if totals["errors"] <= 5:
                        print(f"    Erro votação {votacao.get('id')}: {type(e).__name__}: {str(e)[:80]}")

                # Progress report every 20
                if (i + 1) % 20 == 0:
                    await db.flush()
                    print(f"    ... {i + 1}/{len(all_votacoes)} | eventos={totals['events_created']} votos={totals['votes_created']} skip={totals['votes_skipped']} err={totals['errors']}")

            await db.commit()

    await engine.dispose()

    print(f"\n{'=' * 60}")
    print(f"  RESULTADO")
    print(f"{'=' * 60}")
    print(f"  Votações processadas: {len(all_votacoes)}")
    print(f"  Eventos novos criados: {totals['events_created']}")
    print(f"  Votos individuais criados: {totals['votes_created']}")
    print(f"  Votos duplicados (skip): {totals['votes_skipped']}")
    print(f"  Erros: {totals['errors']}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
