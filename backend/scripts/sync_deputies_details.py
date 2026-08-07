"""
Sincronização de detalhes dos deputados — sobrescreve com dados frescos da API.
Execute: python scripts/sync_deputies_details.py [batch_size] [offset]

Atualiza SEMPRE com dados da API (não pula campos preenchidos):
- Escolaridade, gênero, nascimento, naturalidade, foto
- Email e telefone do gabinete
- Nome civil como social_link

Fonte: https://dadosabertos.camara.leg.br/api/v2/deputados/{id}
"""

import asyncio
import os
import sys
from datetime import UTC, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy import select, delete
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
                        stats["errors"] += 1
                        continue

                    updated = False
                    ultimo_status = data.get("ultimoStatus", {}) or {}
                    gabinete = ultimo_status.get("gabinete", {}) or {}

                    # Escolaridade
                    escolaridade = data.get("escolaridade")
                    if escolaridade:
                        dep.education = escolaridade
                        updated = True

                    # Gênero
                    sexo = data.get("sexo")
                    if sexo:
                        dep.gender = "Masculino" if sexo == "M" else "Feminino" if sexo == "F" else sexo
                        updated = True

                    # Data de nascimento
                    nascimento = data.get("dataNascimento")
                    if nascimento:
                        try:
                            dep.birth_date = datetime.strptime(nascimento, "%Y-%m-%d").date()
                            updated = True
                        except ValueError:
                            pass

                    # Município de nascimento
                    municipio = data.get("municipioNascimento")
                    uf_nasc = data.get("ufNascimento")
                    if municipio:
                        dep.birth_place = f"{municipio}/{uf_nasc}" if uf_nasc else municipio
                        updated = True

                    # Cidade de exercício
                    dep.city_name = "Brasília/DF"

                    # Foto atualizada
                    foto = ultimo_status.get("urlFoto")
                    if foto:
                        dep.photo_url = foto
                        updated = True

                    # Limpar biografia que era "Nome civil: X"
                    if dep.biography and dep.biography.startswith("Nome civil:"):
                        dep.biography = None
                        updated = True

                    if updated:
                        stats["updated"] += 1

                    # === CONTATOS (email, telefone, nome civil) ===

                    # Email
                    email = gabinete.get("email") or ultimo_status.get("email")
                    if email:
                        # Remove existente e recria (atualização)
                        await db.execute(
                            delete(PoliticianSocialLink).where(
                                PoliticianSocialLink.politician_id == dep.id,
                                PoliticianSocialLink.platform == "email",
                            )
                        )
                        db.add(PoliticianSocialLink(
                            politician_id=dep.id, platform="email",
                            url=f"mailto:{email}", username=email,
                            is_official=True, source_id="camara_api",
                        ))
                        stats["emails"] += 1

                    # Telefone
                    telefone = gabinete.get("telefone")
                    if telefone:
                        await db.execute(
                            delete(PoliticianSocialLink).where(
                                PoliticianSocialLink.politician_id == dep.id,
                                PoliticianSocialLink.platform == "phone",
                            )
                        )
                        db.add(PoliticianSocialLink(
                            politician_id=dep.id, platform="phone",
                            url=f"tel:{telefone}", username=telefone,
                            is_official=True, source_id="camara_api",
                        ))
                        stats["phones"] += 1

                    # Nome civil
                    nome_civil = data.get("nomeCivil")
                    if nome_civil and nome_civil != dep.full_name:
                        await db.execute(
                            delete(PoliticianSocialLink).where(
                                PoliticianSocialLink.politician_id == dep.id,
                                PoliticianSocialLink.platform == "nome_civil",
                            )
                        )
                        db.add(PoliticianSocialLink(
                            politician_id=dep.id, platform="nome_civil",
                            url=nome_civil, username=nome_civil,
                            is_official=True, source_id="camara_api",
                        ))

                except Exception as e:
                    stats["errors"] += 1
                    if stats["errors"] <= 5:
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
