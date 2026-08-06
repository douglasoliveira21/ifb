"""
Sincronização Senado Federal — Grupo piloto
Execute: python scripts/sync_senado.py

Importa matérias, votações, comissões e discursos de senadores piloto.
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
from app.models.politician import Politician, PoliticalPosition
from app.models.legislative import (
    LegislativeHouse, Legislator, PoliticianLegislativeProfile,
    LegislativeProposition, PropositionAuthor,
    LegislativeVoteEvent, LegislatorVote,
    LegislativeCommittee, CommitteeMembership,
    LegislativeSpeech,
)

settings = get_settings()
SENADO_API = "https://legis.senado.leg.br/dadosabertos"


async def get_or_create_house(db: AsyncSession):
    result = await db.execute(select(LegislativeHouse).where(LegislativeHouse.acronym == "SF"))
    house = result.scalar_one_or_none()
    if not house:
        house = LegislativeHouse(name="Senado Federal", acronym="SF", api_base_url=SENADO_API)
        db.add(house)
        await db.flush()
    return house


async def get_senado_code(politician: Politician, client: httpx.AsyncClient) -> str | None:
    """Find Senado code by searching the API."""
    if politician.source_url and "senado" in str(politician.source_url).lower():
        # Try to extract code from URL
        parts = str(politician.source_url).split("/")
        for p in parts:
            if p.isdigit() and len(p) >= 3:
                return p

    # Search by name
    try:
        resp = await client.get(f"{SENADO_API}/senador/lista/atual", headers={"Accept": "application/json"})
        if resp.status_code != 200:
            return None
        data = resp.json()
        parlamentares = data.get("ListaParlamentarEmExercicio", {}).get("Parlamentares", {}).get("Parlamentar", [])
        for sen in parlamentares:
            ident = sen.get("IdentificacaoParlamentar", {})
            nome = ident.get("NomeParlamentar", "")
            if nome.lower() == politician.full_name.lower() or nome.lower() in politician.full_name.lower():
                return str(ident.get("CodigoParlamentar", ""))
    except Exception:
        pass
    return None


async def ensure_legislator(db: AsyncSession, house, politician: Politician, senado_code: str):
    """Ensure legislator and profile link exist."""
    leg_result = await db.execute(
        select(Legislator).where(Legislator.external_id == senado_code, Legislator.house_id == house.id)
    )
    legislator = leg_result.scalar_one_or_none()
    if not legislator:
        legislator = Legislator(
            house_id=house.id, external_id=senado_code,
            full_name=politician.full_name, state_code=politician.state_code,
            status="active", last_synced_at=datetime.now(UTC),
        )
        db.add(legislator)
        await db.flush()

    profile_result = await db.execute(
        select(PoliticianLegislativeProfile).where(
            PoliticianLegislativeProfile.politician_id == politician.id,
            PoliticianLegislativeProfile.legislator_id == legislator.id,
        )
    )
    if not profile_result.scalar_one_or_none():
        db.add(PoliticianLegislativeProfile(
            politician_id=politician.id, legislator_id=legislator.id,
            house_id=house.id, match_method="name_match", match_confidence=95.0, status="confirmed",
        ))
        await db.flush()
    return legislator


async def sync_materias(db: AsyncSession, house, politician: Politician, senado_code: str, client: httpx.AsyncClient):
    """Sync legislative matters authored by this senator."""
    print(f"    Matérias de {politician.full_name}...")

    resp = await client.get(f"{SENADO_API}/senador/{senado_code}/autorias",
                            headers={"Accept": "application/json"})
    if resp.status_code != 200:
        print(f"      Erro matérias: {resp.status_code}")
        return 0

    data = resp.json()
    # Navigate nested structure - key is MateriasAutoriaParlamentar
    parl = data.get("MateriasAutoriaParlamentar", data.get("MateriasAutoria", {}))
    if isinstance(parl, dict):
        parl = parl.get("Parlamentar", parl)
    autorias_container = parl.get("Autorias", {}) if isinstance(parl, dict) else {}
    autorias = autorias_container.get("Autoria", []) if isinstance(autorias_container, dict) else []
    if isinstance(autorias, dict):
        autorias = [autorias]

    created = 0
    for a in autorias[:50]:
        materia = a.get("Materia", a)
        ext_id = str(materia.get("Codigo", "") or materia.get("CodigoMateria", ""))
        if not ext_id:
            continue

        existing = await db.execute(
            select(LegislativeProposition).where(
                LegislativeProposition.external_id == ext_id, LegislativeProposition.house_id == house.id
            )
        )
        if existing.scalar_one_or_none():
            continue

        prop = LegislativeProposition(
            house_id=house.id, external_id=ext_id,
            type_acronym=materia.get("Sigla", "") or materia.get("SiglaSubtipoMateria", ""),
            number=int(materia.get("Numero", 0) or materia.get("NumeroMateria", 0) or 0) or None,
            year=int(materia.get("Ano", 0) or materia.get("AnoMateria", 0) or 0) or None,
            title=(materia.get("Ementa") or materia.get("EmentaMateria") or "")[:1000],
            status=materia.get("DescricaoIdentificacao"),
            source_url=f"https://www25.senado.leg.br/web/atividade/materias/-/materia/{ext_id}",
            last_synced_at=datetime.now(UTC),
        )
        db.add(prop)
        await db.flush()

        db.add(PropositionAuthor(
            proposition_id=prop.id, author_name=politician.full_name,
            author_type="legislator", is_primary=True,
        ))
        created += 1

    await db.flush()
    print(f"      {created} matérias criadas (total API: {len(autorias)})")
    return created


async def sync_votes_senado(db: AsyncSession, house, politician: Politician, senado_code: str, legislator: Legislator, client: httpx.AsyncClient):
    """Sync votes for this senator."""
    print(f"    Votações de {politician.full_name}...")

    resp = await client.get(f"{SENADO_API}/senador/{senado_code}/votacoes",
                            headers={"Accept": "application/json"})
    if resp.status_code != 200:
        print(f"      Erro votações: {resp.status_code}")
        return 0

    data = resp.json()
    votacoes = data.get("VotacaoParlamentar", {}).get("Parlamentar", {}).get("Votacoes", {}).get("Votacao", [])
    if isinstance(votacoes, dict):
        votacoes = [votacoes]

    created = 0
    for v in votacoes[:30]:
        ext_id = str(v.get("CodigoSessaoVotacao", "") or v.get("CodigoVotacao", ""))
        if not ext_id:
            continue

        # Get or create vote event
        existing_event = await db.execute(
            select(LegislativeVoteEvent).where(
                LegislativeVoteEvent.external_id == ext_id, LegislativeVoteEvent.house_id == house.id
            )
        )
        event = existing_event.scalar_one_or_none()
        if not event:
            date_raw = v.get("DataSessao")
            date_parsed = None
            if date_raw:
                try:
                    from datetime import datetime as dt
                    date_parsed = dt.strptime(date_raw, "%d/%m/%Y")
                except (ValueError, AttributeError):
                    try:
                        date_parsed = dt.fromisoformat(date_raw.replace("Z", "+00:00"))
                    except:
                        pass

            event = LegislativeVoteEvent(
                house_id=house.id, external_id=ext_id,
                date=date_parsed, description=v.get("DescricaoVotacao", "")[:500] or None,
                result=v.get("Resultado"), is_nominal=True,
                source_url=f"https://www25.senado.leg.br/web/atividade/materias",
            )
            db.add(event)
            await db.flush()

        # Check duplicate vote
        existing_vote = await db.execute(
            select(LegislatorVote).where(
                LegislatorVote.vote_event_id == event.id, LegislatorVote.legislator_id == legislator.id
            )
        )
        if existing_vote.scalar_one_or_none():
            continue

        original = v.get("DescricaoVoto", "Não informado")
        vote_map = {"Sim": "yes", "Não": "no", "Abstenção": "abstention",
                    "NCom": "absent", "Obstrução": "obstruction",
                    "P-NRV": "president", "MIS": "absent", "AP": "absent", "Presidente": "president"}
        normalized = vote_map.get(original, "other")

        db.add(LegislatorVote(
            vote_event_id=event.id, legislator_id=legislator.id,
            original_vote=original, normalized_vote=normalized,
            party_at_vote=politician.state_code,  # Use state as proxy since we don't have party at time
            state_at_vote=politician.state_code,
        ))
        created += 1

    await db.flush()
    print(f"      {created} votos registrados (total API: {len(votacoes)})")
    return created


async def sync_committees_senado(db: AsyncSession, house, politician: Politician, senado_code: str, legislator: Legislator, client: httpx.AsyncClient):
    """Sync committee memberships."""
    print(f"    Comissões de {politician.full_name}...")

    resp = await client.get(f"{SENADO_API}/senador/{senado_code}/comissoes",
                            headers={"Accept": "application/json"})
    if resp.status_code != 200:
        print(f"      Erro comissões: {resp.status_code}")
        return 0

    data = resp.json()
    comissoes = data.get("MembroComissaoParlamentar", {}).get("Parlamentar", {}).get("MembroComissoes", {}).get("Comissao", [])
    if isinstance(comissoes, dict):
        comissoes = [comissoes]

    created = 0
    for c in comissoes[:20]:
        # Get committee identifiers
        ident = c.get("IdentificacaoComissao", {})
        ext_id = str(ident.get("CodigoComissao", ""))
        if not ext_id:
            continue

        existing = await db.execute(
            select(LegislativeCommittee).where(
                LegislativeCommittee.external_id == ext_id, LegislativeCommittee.house_id == house.id
            )
        )
        committee = existing.scalar_one_or_none()
        if not committee:
            committee = LegislativeCommittee(
                house_id=house.id, external_id=ext_id,
                name=(ident.get("NomeComissao") or "")[:500],
                acronym=ident.get("SiglaComissao"),
                committee_type="commission",
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
            participacao = c.get("Participacao", "Membro")
            if isinstance(participacao, list):
                participacao = participacao[0] if participacao else "Membro"
            if isinstance(participacao, dict):
                participacao = participacao.get("DescricaoParticipacao", "Membro")
            db.add(CommitteeMembership(
                committee_id=committee.id, legislator_id=legislator.id,
                role=str(participacao)[:100] if participacao else "Membro",
            ))
            created += 1

    await db.flush()
    print(f"      {created} comissões vinculadas (total API: {len(comissoes)})")
    return created


async def sync_speeches_senado(db: AsyncSession, house, politician: Politician, senado_code: str, legislator: Legislator, client: httpx.AsyncClient):
    """Sync speeches/pronunciamentos."""
    print(f"    Discursos de {politician.full_name}...")

    resp = await client.get(f"{SENADO_API}/senador/{senado_code}/discursos",
                            headers={"Accept": "application/json"})
    if resp.status_code != 200:
        print(f"      Erro discursos: {resp.status_code}")
        return 0

    data = resp.json()
    # Navigate nested JSON
    parl = data.get("DiscursosParlamentar", {}).get("Parlamentar", {})
    pronunc = parl.get("Pronunciamentos")
    if not pronunc or not isinstance(pronunc, dict):
        print(f"      Sem discursos disponíveis")
        return 0
    discursos_path = pronunc.get("Pronunciamento", [])
    if isinstance(discursos_path, dict):
        discursos_path = [discursos_path]

    created = 0
    for d in discursos_path[:20]:
        ext_id = str(d.get("CodigoPronunciamento", ""))
        if not ext_id:
            continue

        existing = await db.execute(
            select(LegislativeSpeech).where(
                LegislativeSpeech.external_id == ext_id, LegislativeSpeech.house_id == house.id
            )
        )
        if existing.scalar_one_or_none():
            continue

        date_raw = d.get("DataPronunciamento")
        date_parsed = None
        if date_raw:
            try:
                from datetime import datetime as dt
                date_parsed = dt.strptime(date_raw, "%d/%m/%Y").date()
            except:
                pass

        speech = LegislativeSpeech(
            house_id=house.id, legislator_id=legislator.id,
            external_id=ext_id, date=date_parsed,
            session_type=d.get("TipoPronunciamento"),
            summary=(d.get("TextoResumo") or d.get("Indexacao") or "")[:2000] or None,
            full_text_url=d.get("UrlTexto"),
            source_url=f"https://www25.senado.leg.br/web/atividade/pronunciamentos/-/p/texto/{ext_id}",
        )
        db.add(speech)
        created += 1

    await db.flush()
    print(f"      {created} discursos importados (total API: {len(discursos_path)})")
    return created


async def main():
    print("\n" + "=" * 60)
    print("  SINCRONIZAÇÃO SENADO — Grupo Piloto")
    print("=" * 60 + "\n")

    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(engine, class_=AsyncSession)

    async with factory() as db:
        house = await get_or_create_house(db)

        # Get 5 pilot senators
        pos_result = await db.execute(
            select(PoliticalPosition.id).where(PoliticalPosition.name == "Senador")
        )
        pos_id = pos_result.scalar_one_or_none()

        pilots_result = await db.execute(
            select(Politician).where(
                Politician.current_position_id == pos_id,
                Politician.is_public == True,
            ).limit(5)
        )
        pilots = pilots_result.scalars().all()

        print(f"  Senadores piloto: {len(pilots)}")
        for p in pilots:
            print(f"    - {p.full_name} ({p.state_code})")

        totals = {"materias": 0, "votos": 0, "comissoes": 0, "discursos": 0}

        async with httpx.AsyncClient(timeout=30, headers={"Accept": "application/json"}) as client:
            for politician in pilots:
                senado_code = await get_senado_code(politician, client)
                if not senado_code:
                    print(f"\n  ⚠ Sem código Senado: {politician.full_name}")
                    continue

                print(f"\n  [{politician.full_name}] (Código: {senado_code})")
                legislator = await ensure_legislator(db, house, politician, senado_code)

                totals["materias"] += await sync_materias(db, house, politician, senado_code, client)
                totals["votos"] += await sync_votes_senado(db, house, politician, senado_code, legislator, client)
                totals["comissoes"] += await sync_committees_senado(db, house, politician, senado_code, legislator, client)
                totals["discursos"] += await sync_speeches_senado(db, house, politician, senado_code, legislator, client)

                await asyncio.sleep(1)  # Rate limit

        await db.commit()

    await engine.dispose()

    print("\n" + "=" * 60)
    print("  RESULTADO SENADO")
    print("=" * 60)
    for k, v in totals.items():
        print(f"  {k}: {v}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
