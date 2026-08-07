"""
Atualiza IDs dos deputados para a legislatura 57 (atual).
Execute: python scripts/update_deputy_ids.py

Os IDs da API da Câmara mudam a cada legislatura.
Este script busca o ID correto da legislatura 57 e atualiza source_url e photo_url.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.politician import Politician, PoliticalPosition

settings = get_settings()
CAMARA_API = "https://dadosabertos.camara.leg.br/api/v2"


async def main():
    print(f"\n{'=' * 60}")
    print(f"  ATUALIZANDO IDS PARA LEGISLATURA 57")
    print(f"{'=' * 60}\n")

    engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=2)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Fetch all current deputies from API (legislatura 57)
    print("  Buscando deputados da legislatura 57 na API...")
    all_api_deputies: list[dict] = []
    async with httpx.AsyncClient(timeout=30, headers={"Accept": "application/json"}) as client:
        page = 1
        while True:
            resp = await client.get(f"{CAMARA_API}/deputados", params={
                "idLegislatura": "57", "itens": "100", "pagina": str(page), "ordem": "ASC", "ordenarPor": "nome"
            })
            if resp.status_code != 200:
                print(f"  Erro página {page}: {resp.status_code}")
                break
            data = resp.json().get("dados", [])
            if not data:
                break
            all_api_deputies.extend(data)
            if len(data) < 100:
                break
            page += 1
            await asyncio.sleep(0.3)

    print(f"  Deputados na API (leg 57): {len(all_api_deputies)}")

    # Build lookup by name
    api_by_name: dict[str, dict] = {}
    for dep in all_api_deputies:
        name = dep.get("nome", "").strip().lower()
        api_by_name[name] = dep

    async with factory() as db:
        pos_r = await db.execute(
            select(PoliticalPosition.id).where(PoliticalPosition.name == "Deputado Federal")
        )
        pos_id = pos_r.scalar_one_or_none()

        deps_r = await db.execute(
            select(Politician).where(
                Politician.current_position_id == pos_id,
                Politician.is_public == True,
            ).order_by(Politician.full_name)
        )
        deputies = deps_r.scalars().all()
        print(f"  Deputados no banco: {len(deputies)}\n")

        stats = {"updated": 0, "not_found": 0, "already_correct": 0}

        for dep in deputies:
            name_lower = dep.full_name.strip().lower()
            # Try exact match
            api_dep = api_by_name.get(name_lower)

            # Try ballot name
            if not api_dep and dep.ballot_name:
                api_dep = api_by_name.get(dep.ballot_name.strip().lower())

            if not api_dep:
                stats["not_found"] += 1
                continue

            new_id = str(api_dep["id"])
            new_url = f"{CAMARA_API}/deputados/{new_id}"
            new_photo = api_dep.get("urlFoto")

            if dep.source_url == new_url:
                stats["already_correct"] += 1
                continue

            # Update
            dep.source_url = new_url
            if new_photo:
                dep.photo_url = new_photo
            stats["updated"] += 1

        await db.commit()

    await engine.dispose()

    print(f"{'=' * 60}")
    print(f"  RESULTADO")
    print(f"{'=' * 60}")
    print(f"  Atualizados: {stats['updated']}")
    print(f"  Já corretos: {stats['already_correct']}")
    print(f"  Não encontrados: {stats['not_found']}")
    print(f"{'=' * 60}\n")
    print("  Agora rode: python scripts/sync_expenses_camara.py 2025 50 0")


if __name__ == "__main__":
    asyncio.run(main())
