"""
Validação das abas legislativas — Deputados piloto
Execute: python scripts/validate_legislative.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

BASE = "http://localhost:8000"
PILOTS = ["acacio-favacho", "adail-filho", "adilson-barroso", "adolfo-viana", "adriana-ventura"]


async def main():
    print("\n" + "=" * 60)
    print("  VALIDAÇÃO LEGISLATIVA — Frontend/API")
    print("=" * 60)

    ok = 0
    fail = 0

    async with httpx.AsyncClient(base_url=BASE, timeout=15) as client:
        for slug in PILOTS:
            print(f"\n  [{slug}]")

            # Propositions
            r = await client.get(f"/api/v1/politicians/{slug}/propositions")
            if r.status_code == 200:
                data = r.json()
                items = data.get("data", [])
                total = data.get("pagination", {}).get("total", len(items))
                print(f"    ✅ Projetos: {len(items)} items (total={total})")
                if items:
                    p = items[0]
                    has_type = bool(p.get("type") or p.get("type_acronym"))
                    has_year = bool(p.get("year"))
                    has_title = bool(p.get("title"))
                    print(f"       Campos: type={has_type}, year={has_year}, title={has_title}")
                    if p.get("source_url"):
                        print(f"       Fonte: {p['source_url'][:60]}")
                ok += 1
            else:
                print(f"    ❌ Projetos: status={r.status_code}")
                fail += 1

            # Votes
            r = await client.get(f"/api/v1/politicians/{slug}/votes")
            if r.status_code == 200:
                data = r.json()
                items = data.get("data", [])
                print(f"    ✅ Votações: {len(items)} votos")
                if items:
                    v = items[0]
                    print(f"       Exemplo: {v.get('date','')[:10]} | {v.get('vote','?')} | {(v.get('description',''))[:40]}")
                ok += 1
            else:
                print(f"    ❌ Votações: status={r.status_code}")
                fail += 1

            # Committees
            r = await client.get(f"/api/v1/politicians/{slug}/committees")
            if r.status_code == 200:
                data = r.json()
                items = data.get("data", [])
                print(f"    ✅ Comissões: {len(items)}")
                if items:
                    c = items[0]
                    print(f"       Exemplo: {c.get('committee_name','')[:40]} ({c.get('role','')})")
                ok += 1
            else:
                print(f"    ❌ Comissões: status={r.status_code}")
                fail += 1

            # Expenses
            r = await client.get(f"/api/v1/politicians/{slug}/parliamentary-expenses")
            if r.status_code == 200:
                data = r.json()
                items = data.get("data", [])
                total_amount = data.get("aggregates", {}).get("total_net_amount", 0)
                print(f"    ✅ Gastos: {len(items)} items, total=R${total_amount:,.2f}")
                ok += 1
            else:
                print(f"    ❌ Gastos: status={r.status_code}")
                fail += 1

            # Attendance (should document limitation)
            r = await client.get(f"/api/v1/politicians/{slug}/attendance")
            if r.status_code == 200:
                data = r.json()
                items = data.get("data", [])
                summary = data.get("summary", {})
                print(f"    ⚠️  Presença: {len(items)} registros (limitação da API)")
                ok += 1
            else:
                print(f"    ❌ Presença: status={r.status_code}")
                fail += 1

    print(f"\n{'=' * 60}")
    print(f"  RESULTADO: ✅ {ok} | ❌ {fail}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
