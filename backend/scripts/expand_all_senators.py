"""
Expansão: Matérias, Votações, Comissões e Discursos para TODOS os senadores.
Execute: python scripts/expand_all_senators.py [batch_size] [offset]

Exemplo: python scripts/expand_all_senators.py 10 0
         python scripts/expand_all_senators.py 10 10
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
    LegislativeVoteEvent, LegislatorVote,
    LegislativeCommittee, CommitteeMembership,
    LegislativeSpeech,
)

settings = get_settings()
SENADO_API = "https://legis.senado.leg.br/dadosabertos"

BATCH_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 10
OFFSET = int(sys.argv[2]) if len(sys.argv) > 2 else 0


async def find_senado_code(name: str, senators_cache: list) -> str | None:
    """Find senator code from cached list."""
    name_lower = name.lower().strip()
    for sen in senators_cache:
        ident = sen.get("IdentificacaoParlamentar", {})
        nome = ident.get("NomeParlamentar", "").lower().strip()
        if nome == name_lower or name_lower in nome or nome in name_lower:
            return str(ident.get("CodigoParlamentar", ""))
    return None


async def main():
    print(f"\n{'='*60}")
    print(f"  EXPANSÃO SENADO (batch={BATCH_SIZE}, offset={OFFSET})")
    print(f"{'='*60}\n")

    engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=2)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Fetch all current senators once
    print("  Buscando lista de senadores na API...")
    async with httpx.AsyncClient(timeout=30, headers={"Accept": "application/json"}) as client:
        resp = await client.get(f"{SENADO_API}/senador/lista/atual")
        if resp.status_code != 200:
            print(f"  Erro ao buscar lista: {resp.status_code}")
            return
        data = resp.json()
        senators_api = data.get("ListaParlamentarEmExercicio", {}).get("Parlamentares", {}).get("Parlamentar", [])
    print(f"  Senadores na API: {len(senators_api)}")

    async with factory() as db:
        # Get house
        house_r = await db.execute(select(LegislativeHouse).where(LegislativeHouse.acronym == "SF"))
        house = house_r.scalar_one_or_none()
        if not house:
            house = LegislativeHouse(name="Senado Federal", acronym="SF", api_base_url=SENADO_API)
            db.add(house)
            await db.flush()

        # Get senators from DB
        pos_r = await db.execute(select(PoliticalPosition.id).where(PoliticalPosition.name == "Senador"))
        pos_id = pos_r.scalar_one_or_none()

        total_r = await db.execute(select(func.count(Politician.id)).where(
            Politician.current_position_id == pos_id, Politician.is_public == True
        ))
        total_in_db = total_r.scalar_one()

        sens_r = await db.execute(
            select(Politician).where(
                Politician.current_position_id == pos_id, Politician.is_public == True,
            ).order_by(Politician.full_name).offset(OFFSET).limit(BATCH_SIZE)
        )
        senators = sens_r.scalars().all()

        print(f"  Total senadores no banco: {total_in_db}")
        print(f"  Processando: {len(senators)} (offset={OFFSET})\n")

        stats = {"materias": 0, "votos": 0, "comissoes": 0, "discursos": 0,
                 "errors": 0, "not_found": 0, "processed": 0}

        async with httpx.AsyncClient(timeout=30, headers={"Accept": "application/json"}) as client:
            for i, pol in enumerate(senators):
                code = await find_senado_code(pol.full_name, senators_api)
                if not code:
                    stats["not_found"] += 1
                    if stats["not_found"] <= 3:
                        print(f"  ⚠ Não encontrado: {pol.full_name}")
                    continue

                # Ensure legislator + profile
                leg_r = await db.execute(select(Legislator).where(
                    Legislator.external_id == code, Legislator.house_id == house.id
                ))
                legislator = leg_r.scalar_one_or_none()
                if not legislator:
                    legislator = Legislator(house_id=house.id, external_id=code,
                                           full_name=pol.full_name, state_code=pol.state_code,
                                           status="active", last_synced_at=datetime.now(UTC))
                    db.add(legislator)
                    await db.flush()

                prof_r = await db.execute(select(PoliticianLegislativeProfile).where(
                    PoliticianLegislativeProfile.politician_id == pol.id,
                    PoliticianLegislativeProfile.legislator_id == legislator.id,
                ))
                if not prof_r.scalar_one_or_none():
                    db.add(PoliticianLegislativeProfile(
                        politician_id=pol.id, legislator_id=legislator.id,
                        house_id=house.id, match_method="name_match",
                        match_confidence=95.0, status="confirmed",
                    ))
                    await db.flush()

                try:
                    # Matérias
                    r = await client.get(f"{SENADO_API}/senador/{code}/autorias")
                    if r.status_code == 200:
                        parl = r.json().get("MateriasAutoriaParlamentar", {}).get("Parlamentar", {})
                        autorias = parl.get("Autorias", {}).get("Autoria", []) if isinstance(parl.get("Autorias"), dict) else []
                        if isinstance(autorias, dict): autorias = [autorias]
                        for a in autorias[:30]:
                            mat = a.get("Materia", a)
                            ext_id = str(mat.get("Codigo", ""))
                            if not ext_id: continue
                            ex = await db.execute(select(LegislativeProposition.id).where(
                                LegislativeProposition.external_id == ext_id, LegislativeProposition.house_id == house.id
                            ))
                            if not ex.scalar_one_or_none():
                                prop = LegislativeProposition(
                                    house_id=house.id, external_id=ext_id,
                                    type_acronym=mat.get("Sigla", ""), number=int(mat.get("Numero", 0) or 0) or None,
                                    year=int(mat.get("Ano", 0) or 0) or None,
                                    title=(mat.get("Ementa") or "")[:1000],
                                    source_url=f"https://www25.senado.leg.br/web/atividade/materias/-/materia/{ext_id}",
                                    last_synced_at=datetime.now(UTC),
                                )
                                db.add(prop)
                                await db.flush()
                                db.add(PropositionAuthor(proposition_id=prop.id, author_name=pol.full_name, author_type="legislator", is_primary=True))
                                stats["materias"] += 1

                    # Votações
                    r2 = await client.get(f"{SENADO_API}/senador/{code}/votacoes")
                    if r2.status_code == 200:
                        votacoes = r2.json().get("VotacaoParlamentar", {}).get("Parlamentar", {}).get("Votacoes", {}).get("Votacao", [])
                        if isinstance(votacoes, dict): votacoes = [votacoes]
                        for v in votacoes[:30]:
                            ext_id = str(v.get("CodigoSessaoVotacao", "") or v.get("CodigoVotacao", ""))
                            if not ext_id: continue
                            ev_r = await db.execute(select(LegislativeVoteEvent).where(
                                LegislativeVoteEvent.external_id == ext_id, LegislativeVoteEvent.house_id == house.id
                            ))
                            event = ev_r.scalar_one_or_none()
                            if not event:
                                date_raw = v.get("DataSessao")
                                date_parsed = None
                                if date_raw:
                                    try:
                                        from datetime import datetime as dt
                                        date_parsed = dt.strptime(date_raw, "%d/%m/%Y")
                                    except: pass
                                event = LegislativeVoteEvent(house_id=house.id, external_id=ext_id,
                                    date=date_parsed, description=(v.get("DescricaoVotacao") or "")[:500] or None,
                                    result=v.get("Resultado"), is_nominal=True,
                                    source_url=f"https://www25.senado.leg.br/web/atividade/materias")
                                db.add(event)
                                await db.flush()
                            vt_r = await db.execute(select(LegislatorVote.id).where(
                                LegislatorVote.vote_event_id == event.id, LegislatorVote.legislator_id == legislator.id
                            ))
                            if not vt_r.scalar_one_or_none():
                                original = v.get("DescricaoVoto", "Não informado")
                                norm_map = {"Sim": "yes", "Não": "no", "Abstenção": "abstention", "NCom": "absent", "Obstrução": "obstruction", "P-NRV": "president", "Presidente": "president"}
                                db.add(LegislatorVote(vote_event_id=event.id, legislator_id=legislator.id,
                                    original_vote=original, normalized_vote=norm_map.get(original, "other"),
                                    state_at_vote=pol.state_code))
                                stats["votos"] += 1

                    # Comissões
                    r3 = await client.get(f"{SENADO_API}/senador/{code}/comissoes")
                    if r3.status_code == 200:
                        comissoes = r3.json().get("MembroComissaoParlamentar", {}).get("Parlamentar", {}).get("MembroComissoes", {}).get("Comissao", [])
                        if isinstance(comissoes, dict): comissoes = [comissoes]
                        for c in comissoes[:20]:
                            ident = c.get("IdentificacaoComissao", {})
                            ext_id = str(ident.get("CodigoComissao", ""))
                            if not ext_id: continue
                            com_r = await db.execute(select(LegislativeCommittee).where(
                                LegislativeCommittee.external_id == ext_id, LegislativeCommittee.house_id == house.id
                            ))
                            committee = com_r.scalar_one_or_none()
                            if not committee:
                                committee = LegislativeCommittee(house_id=house.id, external_id=ext_id,
                                    name=(ident.get("NomeComissao") or "")[:500], acronym=ident.get("SiglaComissao"))
                                db.add(committee)
                                await db.flush()
                            mem_r = await db.execute(select(CommitteeMembership.id).where(
                                CommitteeMembership.committee_id == committee.id, CommitteeMembership.legislator_id == legislator.id
                            ))
                            if not mem_r.scalar_one_or_none():
                                part = c.get("Participacao", "Membro")
                                if isinstance(part, list): part = part[0] if part else "Membro"
                                if isinstance(part, dict): part = part.get("DescricaoParticipacao", "Membro")
                                db.add(CommitteeMembership(committee_id=committee.id, legislator_id=legislator.id, role=str(part)[:100]))
                                stats["comissoes"] += 1

                    # Discursos
                    r4 = await client.get(f"{SENADO_API}/senador/{code}/discursos")
                    if r4.status_code == 200:
                        parl4 = r4.json().get("DiscursosParlamentar", {}).get("Parlamentar", {})
                        pronunc = parl4.get("Pronunciamentos")
                        if pronunc and isinstance(pronunc, dict):
                            discs = pronunc.get("Pronunciamento", [])
                            if isinstance(discs, dict): discs = [discs]
                            for d in discs[:10]:
                                d_ext = str(d.get("CodigoPronunciamento", ""))
                                if not d_ext: continue
                                d_r = await db.execute(select(LegislativeSpeech.id).where(
                                    LegislativeSpeech.external_id == d_ext, LegislativeSpeech.house_id == house.id
                                ))
                                if not d_r.scalar_one_or_none():
                                    date_raw = d.get("DataPronunciamento")
                                    date_p = None
                                    if date_raw:
                                        try:
                                            from datetime import datetime as dt
                                            date_p = dt.strptime(date_raw, "%d/%m/%Y").date()
                                        except: pass
                                    db.add(LegislativeSpeech(house_id=house.id, legislator_id=legislator.id,
                                        external_id=d_ext, date=date_p, session_type=d.get("TipoPronunciamento"),
                                        summary=(d.get("TextoResumo") or d.get("Indexacao") or "")[:2000] or None,
                                        full_text_url=d.get("UrlTexto"),
                                        source_url=f"https://www25.senado.leg.br/web/atividade/pronunciamentos/-/p/texto/{d_ext}"))
                                    stats["discursos"] += 1

                    stats["processed"] += 1
                except Exception as e:
                    stats["errors"] += 1
                    if stats["errors"] <= 5:
                        print(f"  Erro {pol.full_name}: {type(e).__name__}: {str(e)[:80]}")

                if (i + 1) % 5 == 0:
                    await db.flush()
                    print(f"  ... {i+1}/{len(senators)} | mat={stats['materias']} vot={stats['votos']} com={stats['comissoes']} disc={stats['discursos']} err={stats['errors']}")

                await asyncio.sleep(1)

        await db.commit()

    await engine.dispose()

    print(f"\n{'='*60}")
    print(f"  RESULTADO SENADO")
    print(f"{'='*60}")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"\n  Próximo: python scripts/expand_all_senators.py {BATCH_SIZE} {OFFSET + BATCH_SIZE}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
