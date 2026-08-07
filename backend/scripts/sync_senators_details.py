"""
Sincronização de detalhes dos senadores — biografia, contato, município, nascimento.
Execute: python scripts/sync_senators_details.py [batch_size] [offset]

Atualiza cada senador com dados completos da API do Senado:
- Dados pessoais (nome civil, nascimento, naturalidade)
- Contato (email, telefone)
- Foto atualizada

Fonte: https://legis.senado.leg.br/dadosabertos/senador/{codigo}
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
from app.models.politician import Politician, PoliticalPosition, PoliticianSocialLink

settings = get_settings()
SENADO_API = "https://legis.senado.leg.br/dadosabertos"

BATCH_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 30
OFFSET = int(sys.argv[2]) if len(sys.argv) > 2 else 0


async def find_senado_code(name: str, senators_cache: list) -> str | None:
    """Encontra código do senador na lista da API."""
    name_lower = name.lower().strip()
    for sen in senators_cache:
        ident = sen.get("IdentificacaoParlamentar", {})
        nome = ident.get("NomeParlamentar", "").lower().strip()
        if nome == name_lower or name_lower in nome or nome in name_lower:
            return str(ident.get("CodigoParlamentar", ""))
    return None


async def main():
    print(f"\n{'=' * 60}")
    print(f"  DETALHES DOS SENADORES (batch={BATCH_SIZE}, offset={OFFSET})")
    print(f"{'=' * 60}\n")

    engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=2)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Fetch current senators list
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
        # Get senators from DB
        pos_r = await db.execute(
            select(PoliticalPosition.id).where(PoliticalPosition.name == "Senador")
        )
        pos_id = pos_r.scalar_one_or_none()
        if not pos_id:
            print("  Cargo 'Senador' não encontrado.")
            return

        sens_r = await db.execute(
            select(Politician).where(
                Politician.current_position_id == pos_id,
                Politician.is_public == True,
            ).order_by(Politician.full_name).offset(OFFSET).limit(BATCH_SIZE)
        )
        senators = sens_r.scalars().all()
        print(f"  Processando {len(senators)} senadores (offset={OFFSET})\n")

        stats = {"updated": 0, "emails": 0, "phones": 0, "not_found": 0, "errors": 0}

        async with httpx.AsyncClient(timeout=30, headers={"Accept": "application/json"}) as client:
            for i, sen in enumerate(senators):
                code = await find_senado_code(sen.full_name, senators_api)
                if not code:
                    stats["not_found"] += 1
                    continue

                try:
                    # Fetch senator details
                    resp = await client.get(f"{SENADO_API}/senador/{code}")
                    if resp.status_code != 200:
                        stats["errors"] += 1
                        continue

                    data = resp.json()
                    parl = data.get("DetalheParlamentar", {}).get("Parlamentar", {})
                    if not parl:
                        continue

                    ident = parl.get("IdentificacaoParlamentar", {})
                    dados_basicos = parl.get("DadosBasicosParlamentar", {})

                    updated = False

                    # Nome civil
                    nome_civil = ident.get("NomeCompletoParlamentar")
                    if nome_civil and not sen.biography:
                        sen.biography = f"Nome civil: {nome_civil}"
                        updated = True

                    # Nascimento
                    nascimento = dados_basicos.get("DataNascimento")
                    if nascimento and not sen.birth_date:
                        try:
                            sen.birth_date = datetime.strptime(nascimento, "%Y-%m-%d").date()
                            updated = True
                        except ValueError:
                            try:
                                sen.birth_date = datetime.strptime(nascimento, "%d/%m/%Y").date()
                                updated = True
                            except ValueError:
                                pass

                    # Naturalidade
                    naturalidade = dados_basicos.get("Naturalidade")
                    uf_nasc = dados_basicos.get("UfNaturalidade")
                    if naturalidade and not sen.birth_place:
                        sen.birth_place = f"{naturalidade}/{uf_nasc}" if uf_nasc else naturalidade
                        updated = True

                    # Foto
                    foto = ident.get("UrlFotoParlamentar")
                    if foto and foto != sen.photo_url:
                        sen.photo_url = foto
                        updated = True

                    # Cidade (exercício)
                    if not sen.city_name:
                        sen.city_name = "Brasília/DF"
                        updated = True

                    # Sexo
                    sexo = dados_basicos.get("Sexo") or ident.get("SexoParlamentar")
                    if sexo and not sen.gender:
                        sen.gender = "Masculino" if sexo in ("M", "Masculino") else "Feminino" if sexo in ("F", "Feminino") else sexo
                        updated = True

                    if updated:
                        stats["updated"] += 1

                    # Email
                    email = ident.get("EmailParlamentar")
                    if email:
                        existing = await db.execute(
                            select(PoliticianSocialLink).where(
                                PoliticianSocialLink.politician_id == sen.id,
                                PoliticianSocialLink.platform == "email",
                            )
                        )
                        if not existing.scalar_one_or_none():
                            db.add(PoliticianSocialLink(
                                politician_id=sen.id,
                                platform="email",
                                url=f"mailto:{email}",
                                username=email,
                                is_official=True,
                                source_id="senado_api",
                            ))
                            stats["emails"] += 1

                    # Telefone
                    telefones = parl.get("Telefones", {})
                    tel_list = telefones.get("Telefone", []) if isinstance(telefones, dict) else []
                    if isinstance(tel_list, dict):
                        tel_list = [tel_list]
                    if tel_list:
                        tel = tel_list[0]
                        numero = tel.get("NumeroTelefone", "")
                        if numero:
                            existing_phone = await db.execute(
                                select(PoliticianSocialLink).where(
                                    PoliticianSocialLink.politician_id == sen.id,
                                    PoliticianSocialLink.platform == "phone",
                                )
                            )
                            if not existing_phone.scalar_one_or_none():
                                db.add(PoliticianSocialLink(
                                    politician_id=sen.id,
                                    platform="phone",
                                    url=f"tel:{numero}",
                                    username=numero,
                                    is_official=True,
                                    source_id="senado_api",
                                ))
                                stats["phones"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    if stats["errors"] <= 3:
                        print(f"  Erro {sen.full_name}: {e}")

                if (i + 1) % 10 == 0:
                    await db.flush()
                    print(f"  ... {i+1}/{len(senators)} | updated={stats['updated']} emails={stats['emails']} phones={stats['phones']}")

                await asyncio.sleep(0.5)

        await db.commit()

    await engine.dispose()

    print(f"\n{'=' * 60}")
    print(f"  RESULTADO")
    print(f"{'=' * 60}")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"\n  Próximo: python scripts/sync_senators_details.py {BATCH_SIZE} {OFFSET + BATCH_SIZE}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
