"""
Sincronização legislativa — grupo piloto
Execute: python scripts/sync_legislative.py

Importa proposições, votações e comissões de deputados piloto.
"""

import asyncio
import sys
import os
from datetime import UTC, datetime

# Fix import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.politician import Politician, PoliticalPosition
from app.models.legislative import (
    LegislativeHouse,
    LegislativeProposition,
    LegislativeVoteEvent,
    LegislatorVote,
    LegislativeCommittee,
    CommitteeMembership,
    PropositionAuthor,
    PoliticianLegislativeProfile,
    Legislator,
)

settings = get_settings()
CAMARA_API = "https://dadosabertos.camara.leg.br/api/v2"
SENADO_API = "https://legis.senado.leg.br/dadosabertos"


async def get_or_create_house(db: AsyncSession, acronym: str, name: str, api_url: str):
    result = await db.execute(select(LegislativeHouse).where(LegislativeHouse.acronym == acronym))
    house = result.scalar_one_or_none()
    if not house:
        house = LegislativeHouse(name=name, acronym=acronym, api_base_url=api_url)
        db.add(house)
        await db.flush()
    return house


async def get_camara_id(politician: Politician) -> str | None:
    """Extract Câmara deputy ID from source_url."""
    if politician.source_url and "deputados/" in str(politician.source_url):
        parts = str(politician.source_url).split("/")
        for i, p in enumerate(parts):
            if p == "deputados" and i + 1 < len(parts):
                return parts[i + 1]
    return None


async def sync_propositions_camara(db: AsyncSession, house, politician: Politician, camara_id: str, client: httpx.AsyncClient):
    """Sync propositions authored by this deputy."""
    print(f"    Proposições de {politician.full_name}...")

    resp = await client.get(f"{CAMARA_API}/proposicoes", params={
        "idDeputadoAutor": camara_id, "itens": 50, "ordem": "DESC", "ordenarPor": "id"
    })
    if resp.status_code != 200:
        print(f"      Erro: {resp.status_code}")
        return 0

    props = resp.json().get("dados", [])
    created = 0

    for p in props:
        ext_id = str(p.get("id", ""))
        existing = await db.execute(
            select(LegislativeProposition).where(
                LegislativeProposition.external_id == ext_id,
                LegislativeProposition.house_id == house.id,
            )
        )
        if existing.scalar_one_or_none():
            continue

        prop = LegislativeProposition(
            house_id=house.id,
            external_id=ext_id,
            type_acronym=p.get("siglaTipo", ""),
            number=p.get("numero"),
            year=p.get("ano"),
            title=(p.get("ementa") or "")[:1000],
            status=None,
            source_url=p.get("uri"),
            last_synced_at=datetime.now(UTC),
        )
        db.add(prop)
        await db.flush()

        # Link author
        db.add(PropositionAuthor(
            proposition_id=prop.id,
            author_name=politician.full_name,
            author_type="legislator",
            is_primary=True,
        ))
        created += 1

    await db.flush()
    print(f"      {created} proposições criadas (total API: {len(props)})")
    return created


async def sync_votes_camara(db: AsyncSession, house, politician: Politician, camara_id: str, client: httpx.AsyncClient):
    """Sync recent votes for this deputy using global /votacoes endpoint."""
    print(f"    Votações de {politician.full_name}...")

    # Get legislator record
    leg_result = await db.execute(
        select(Legislator).where(Legislator.external_id == camara_id, Legislator.house_id == house.id)
    )
    legislator = leg_result.scalar_one_or_none()
    if not legislator:
        legislator = Legislator(
            house_id=house.id, external_id=camara_id,
            full_name=politician.full_name, state_code=politician.state_code,
            status="active", last_synced_at=datetime.now(UTC),
        )
        db.add(legislator)
        await db.flush()

    # Ensure profile link
    profile_result = await db.execute(
        select(PoliticianLegislativeProfile).where(
            PoliticianLegislativeProfile.politician_id == politician.id,
            PoliticianLegislativeProfile.legislator_id == legislator.id,
        )
    )
    if not profile_result.scalar_one_or_none():
        db.add(PoliticianLegislativeProfile(
            politician_id=politician.id, legislator_id=legislator.id,
            house_id=house.id, match_method="source_url", match_confidence=100.0, status="confirmed",
        ))
        await db.flush()

    # Fetch recent nominal votes from global endpoint
    resp = await client.get(f"{CAMARA_API}/votacoes", params={
        "dataInicio": "2026-03-01", "dataFim": "2026-05-31", "itens": 20,
        "ordem": "DESC", "ordenarPor": "dataHoraRegistro",
    }, headers={"Accept": "application/json"})
    if resp.status_code != 200:
        print(f"      Erro votações global: {resp.status_code} — {resp.text[:100]}")
        return 0

    votes_data = resp.json().get("dados", [])
    created = 0

    for v in votes_data:
        ext_id = str(v.get("id", ""))
        if not ext_id:
            continue

        # Create or get vote event
        existing_event = await db.execute(
            select(LegislativeVoteEvent).where(
                LegislativeVoteEvent.external_id == ext_id, LegislativeVoteEvent.house_id == house.id
            )
        )
        event = existing_event.scalar_one_or_none()
        if not event:
            # Parse date string to datetime
            date_raw = v.get("dataHoraRegistro") or v.get("data")
            date_parsed = None
            if date_raw:
                from datetime import datetime as dt
                try:
                    date_parsed = dt.fromisoformat(date_raw.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

            event = LegislativeVoteEvent(
                house_id=house.id, external_id=ext_id,
                date=date_parsed, description=v.get("descricao"),
                result=str(v.get("aprovacao", "")), is_nominal=True,
                source_url=f"{CAMARA_API}/votacoes/{ext_id}",
            )
            db.add(event)
            await db.flush()

        # Check if vote already recorded for this legislator
        existing_vote = await db.execute(
            select(LegislatorVote).where(
                LegislatorVote.vote_event_id == event.id, LegislatorVote.legislator_id == legislator.id
            )
        )
        if existing_vote.scalar_one_or_none():
            continue

        # Get individual votes for this voting event
        await asyncio.sleep(0.5)  # Rate limit
        vote_detail_resp = await client.get(f"{CAMARA_API}/votacoes/{ext_id}/votos")
        if vote_detail_resp.status_code != 200:
            continue

        all_votes = vote_detail_resp.json().get("dados", [])
        # Find this deputy's vote
        my_vote = None
        for vv in all_votes:
            dep_info = vv.get("deputado_", {})
            if str(dep_info.get("id", "")) == camara_id:
                my_vote = vv
                break

        if my_vote:
            original = my_vote.get("tipoVoto", "Ausente")
            vote_map = {
                "Sim": "yes", "Não": "no", "Abstenção": "abstention",
                "Obstrução": "obstruction", "Art. 17": "art17",
                "Presidente": "president", "-": "absent",
            }
            normalized = vote_map.get(original, "absent")
            db.add(LegislatorVote(
                vote_event_id=event.id, legislator_id=legislator.id,
                original_vote=original, normalized_vote=normalized,
                party_at_vote=my_vote.get("deputado_", {}).get("siglaPartido"),
                state_at_vote=my_vote.get("deputado_", {}).get("siglaUf"),
            ))
            created += 1

    await db.flush()
    print(f"      {created} votos registrados (votações consultadas: {len(votes_data)})")
    return created


async def sync_committees_camara(db: AsyncSession, house, politician: Politician, camara_id: str, client: httpx.AsyncClient):
    """Sync committee memberships."""
    print(f"    Comissões de {politician.full_name}...")

    # Get legislator
    leg_result = await db.execute(
        select(Legislator).where(Legislator.external_id == camara_id, Legislator.house_id == house.id)
    )
    legislator = leg_result.scalar_one_or_none()
    if not legislator:
        return 0

    resp = await client.get(f"{CAMARA_API}/deputados/{camara_id}/orgaos", params={"itens": 50})
    if resp.status_code != 200:
        return 0

    organs = resp.json().get("dados", [])
    created = 0

    for org in organs:
        ext_id = str(org.get("idOrgao", ""))
        # Get or create committee
        existing = await db.execute(
            select(LegislativeCommittee).where(
                LegislativeCommittee.external_id == ext_id, LegislativeCommittee.house_id == house.id
            )
        )
        committee = existing.scalar_one_or_none()
        if not committee:
            committee = LegislativeCommittee(
                house_id=house.id, external_id=ext_id,
                name=org.get("nomeOrgao", "")[:500], acronym=org.get("siglaOrgao"),
                committee_type=org.get("tipoOrgao"),
            )
            db.add(committee)
            await db.flush()

        # Check membership
        mem_exists = await db.execute(
            select(CommitteeMembership).where(
                CommitteeMembership.committee_id == committee.id,
                CommitteeMembership.legislator_id == legislator.id,
            )
        )
        if not mem_exists.scalar_one_or_none():
            db.add(CommitteeMembership(
                committee_id=committee.id, legislator_id=legislator.id,
                role=org.get("titulo", "Membro") or "Membro",
            ))
            created += 1

    await db.flush()
    print(f"      {created} comissões vinculadas (total: {len(organs)})")
    return created


async def main():
    print("\n" + "=" * 60)
    print("  SINCRONIZAÇÃO LEGISLATIVA — Grupo Piloto")
    print("=" * 60 + "\n")

    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(engine, class_=AsyncSession)

    async with factory() as db:
        # Get houses
        house_cd = await get_or_create_house(db, "CD", "Câmara dos Deputados", CAMARA_API)

        # Pilot deputies (first 3 with source_url)
        pos_result = await db.execute(
            select(PoliticalPosition.id).where(PoliticalPosition.name == "Deputado Federal")
        )
        pos_id = pos_result.scalar_one_or_none()

        pilots_result = await db.execute(
            select(Politician).where(
                Politician.current_position_id == pos_id,
                Politician.is_public == True,
                Politician.source_url != None,
            ).limit(5)
        )
        pilots = pilots_result.scalars().all()

        print(f"  Deputados piloto: {len(pilots)}")
        for p in pilots:
            print(f"    - {p.full_name} ({p.state_code})")

        total_props = 0
        total_votes = 0
        total_committees = 0

        async with httpx.AsyncClient(timeout=30, headers={"Accept": "application/json"}) as client:
            for politician in pilots:
                camara_id = await get_camara_id(politician)
                if not camara_id:
                    print(f"  ⚠ Sem ID da Câmara: {politician.full_name}")
                    continue

                print(f"\n  [{politician.full_name}] (ID: {camara_id})")
                total_props += await sync_propositions_camara(db, house_cd, politician, camara_id, client)
                total_votes += await sync_votes_camara(db, house_cd, politician, camara_id, client)
                total_committees += await sync_committees_camara(db, house_cd, politician, camara_id, client)

                # Rate limiting
                await asyncio.sleep(1)

        await db.commit()

    await engine.dispose()

    print("\n" + "=" * 60)
    print("  RESULTADO")
    print("=" * 60)
    print(f"  Proposições: {total_props}")
    print(f"  Votos: {total_votes}")
    print(f"  Comissões: {total_committees}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
