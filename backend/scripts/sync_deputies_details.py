"""
Sincronização de detalhes dos deputados — biografia, contato, município, nascimento.
Execute: python scripts/sync_deputies_details.py [batch_size] [offset]

Atualiza cada deputado com dados completos da API da Câmara:
- Biografia (nomeCivil, escolaridade, dataNascimento, municipioNascimento)
- Contato (email, telefone, gabinete)
- Foto atualizada

Fonte: https://dadosabertos.camara.leg.br/api/v2/deputados/{id}
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
CAMARA_API = "https://dadosabertos.camara.leg.br/api/v2"

BATCH_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 50
OFFSET = int(sys.argv[2]) if len(sys.argv) > 2 else 0


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
    print(f"  DETALHES DOS DEPUTADOS (batch={BATCH_SIZE}, offset={OFFSET})")
    print(f"{'=' * 60}\n")

    engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=2)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as db:
        # Get deputies
        pos_r = await db.execute(
            select(PoliticalPosition.id).where(PoliticalPosition.name == "Deputado Federal")
        )
        pos_id = pos_r.scalar_one_or_none()
        if not pos_id:
            print("  Cargo 'Deputado Federal' não encontrado.")
            return

        deps_r = await db.execute(
            select(Politician).where(
                Politician.current_position_id == pos_id,
                Politician.is_public == True,
                Politician.source_url != None,
            ).order_by(Politician.full_name).offset(OFFSET).limit(BATCH_SIZE)
        )
        deputies = deps_r.scalars().all()
        print(f"  Processando {len(deputies)} deputados (offset={OFFSET})\n")

        stats = {"updated": 0, "emails": 0, "phones": 0, "skipped": 0, "errors": 0}

        async with httpx.AsyncClient(timeout=20, headers={"Accept": "application/json"}) as client:
            for i, dep in enumerate(deputies):
                camara_id = extract_camara_id(dep.source_url)
                if not camara_id:
                    stats["skipped"] += 1
                    continue

                try:
                    resp = await client.get(f"{CAMARA_API}/deputados/{camara_id}")
                    if resp.status_code != 200:
                        stats["errors"] += 1
                        continue

                    data = resp.json().get("dados", {})
                    if not data:
                        continue

                    updated = False

                    # Nome civil → will be shown in sidebar (not biography)
                    nome_civil = data.get("nomeCivil")
                    # We store nomeCivil in birth_place temporarily or as part of the flow
                    # The frontend already shows full_name; nomeCivil goes to social_links
                    if nome_civil and nome_civil != dep.full_name:
                        existing_nc = await db.execute(
                            select(PoliticianSocialLink).where(
                                PoliticianSocialLink.politician_id == dep.id,
                                PoliticianSocialLink.platform == "nome_civil",
                            )
                        )
                        if not existing_nc.scalar_one_or_none():
                            db.add(PoliticianSocialLink(
                                politician_id=dep.id,
                                platform="nome_civil",
                                url=nome_civil,
                                username=nome_civil,
                                is_official=True,
                                source_id="camara_api",
                            ))

                    escolaridade = data.get("escolaridade")
                    if escolaridade and not dep.education:
                        dep.education = escolaridade
                        updated = True

                    sexo = data.get("sexo")
                    if sexo and not dep.gender:
                        dep.gender = "Masculino" if sexo == "M" else "Feminino" if sexo == "F" else sexo
                        updated = True

                    nascimento = data.get("dataNascimento")
                    if nascimento and not dep.birth_date:
                        try:
                            dep.birth_date = datetime.strptime(nascimento, "%Y-%m-%d").date()
                            updated = True
                        except ValueError:
                            pass

                    municipio_nasc = data.get("municipioNascimento")
                    uf_nasc = data.get("ufNascimento")
                    if municipio_nasc and not dep.birth_place:
                        dep.birth_place = f"{municipio_nasc}/{uf_nasc}" if uf_nasc else municipio_nasc
                        updated = True

                    # Gabinete info → city_name (local de exercício)
                    gabinete = data.get("ultimoStatus", {}).get("gabinete", {})
                    if not dep.city_name:
                        dep.city_name = "Brasília/DF"
                        updated = True

                    # Photo
                    photo = data.get("ultimoStatus", {}).get("urlFoto")
                    if photo and photo != dep.photo_url:
                        dep.photo_url = photo
                        updated = True

                    if updated:
                        stats["updated"] += 1

                    # Email
                    email = gabinete.get("email") if gabinete else None
                    if not email:
                        email = data.get("ultimoStatus", {}).get("email")
                    if email:
                        existing_email = await db.execute(
                            select(PoliticianSocialLink).where(
                                PoliticianSocialLink.politician_id == dep.id,
                                PoliticianSocialLink.platform == "email",
                            )
                        )
                        if not existing_email.scalar_one_or_none():
                            db.add(PoliticianSocialLink(
                                politician_id=dep.id,
                                platform="email",
                                url=f"mailto:{email}",
                                username=email,
                                is_official=True,
                                source_id="camara_api",
                            ))
                            stats["emails"] += 1

                    # Phone
                    telefone = gabinete.get("telefone") if gabinete else None
                    if telefone:
                        existing_phone = await db.execute(
                            select(PoliticianSocialLink).where(
                                PoliticianSocialLink.politician_id == dep.id,
                                PoliticianSocialLink.platform == "phone",
                            )
                        )
                        if not existing_phone.scalar_one_or_none():
                            db.add(PoliticianSocialLink(
                                politician_id=dep.id,
                                platform="phone",
                                url=f"tel:{telefone}",
                                username=telefone,
                                is_official=True,
                                source_id="camara_api",
                            ))
                            stats["phones"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    if stats["errors"] <= 3:
                        print(f"  Erro {dep.full_name}: {e}")

                if (i + 1) % 10 == 0:
                    await db.flush()
                    print(f"  ... {i+1}/{len(deputies)} | updated={stats['updated']} emails={stats['emails']} phones={stats['phones']}")

                await asyncio.sleep(0.3)

        await db.commit()

    await engine.dispose()

    print(f"\n{'=' * 60}")
    print(f"  RESULTADO")
    print(f"{'=' * 60}")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"\n  Próximo: python scripts/sync_deputies_details.py {BATCH_SIZE} {OFFSET + BATCH_SIZE}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
