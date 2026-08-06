"""
Script de validação RC1 — Instituto Fiscaliza Brasil
Execute no shell do backend: python scripts/validate_rc1.py
Testa todos os fluxos críticos e gera relatório.
"""

import asyncio
import json
import sys

import httpx

BASE = "http://localhost:8000"
RESULTS = []


def report(test: str, status: str, detail: str = ""):
    icon = "✅" if status == "OK" else "❌" if status == "FAIL" else "⚠️"
    RESULTS.append({"test": test, "status": status, "detail": detail})
    print(f"  {icon} {test}: {detail[:120]}")


async def main():
    print("\n" + "=" * 60)
    print("  VALIDAÇÃO RC1 — Instituto Fiscaliza Brasil")
    print("=" * 60 + "\n")

    async with httpx.AsyncClient(base_url=BASE, timeout=15) as client:

        # 1. Health check
        print("[1] HEALTH CHECK")
        r = await client.get("/api/v1/health")
        if r.status_code == 200 and r.json().get("status") == "healthy":
            report("Health", "OK", f"status={r.json()['status']}")
        else:
            report("Health", "FAIL", f"status_code={r.status_code}")

        # 2. Listagem de políticos
        print("\n[2] LISTAGEM DE POLÍTICOS")
        r = await client.get("/api/v1/politicians?limit=5")
        if r.status_code == 200:
            data = r.json()
            total = data.get("total", 0)
            items = data.get("items", [])
            report("GET /politicians", "OK", f"total={total}, items_returned={len(items)}")
            if total == 0:
                report("Dados existentes", "FAIL", "Nenhum político no banco")
            else:
                report("Dados existentes", "OK", f"{total} políticos cadastrados")
                # Check fields
                p = items[0]
                has_name = bool(p.get("full_name"))
                has_slug = bool(p.get("slug"))
                has_state = bool(p.get("state_code"))
                report("Campos básicos", "OK" if all([has_name, has_slug]) else "WARN",
                       f"name={has_name}, slug={has_slug}, state={has_state}")
        else:
            report("GET /politicians", "FAIL", f"status={r.status_code}, body={r.text[:200]}")

        # 3. Filtro por estado
        print("\n[3] FILTRO POR ESTADO")
        r = await client.get("/api/v1/politicians?state=SP&limit=5")
        if r.status_code == 200:
            data = r.json()
            report("Filtro state=SP", "OK", f"total={data.get('total', 0)}")
        else:
            report("Filtro state=SP", "FAIL", f"status={r.status_code}")

        # 4. Busca por nome
        print("\n[4] BUSCA POR NOME")
        r = await client.get("/api/v1/politicians?q=silva&limit=5")
        if r.status_code == 200:
            data = r.json()
            report("Busca q=silva", "OK", f"total={data.get('total', 0)}")
        else:
            report("Busca q=silva", "FAIL", f"status={r.status_code}")

        # 5. Perfil individual
        print("\n[5] PERFIL INDIVIDUAL")
        # Get first politician slug
        r = await client.get("/api/v1/politicians?limit=1")
        if r.status_code == 200 and r.json().get("items"):
            slug = r.json()["items"][0]["slug"]
            r2 = await client.get(f"/api/v1/politicians/{slug}")
            if r2.status_code == 200:
                profile = r2.json()
                report(f"GET /politicians/{slug}", "OK",
                       f"name={profile.get('full_name')}, party={profile.get('current_party')}")
            else:
                report(f"GET /politicians/{slug}", "FAIL", f"status={r2.status_code}, body={r2.text[:200]}")
        else:
            report("Perfil individual", "FAIL", "Sem políticos para testar")

        # 6. Abas do perfil
        print("\n[6] ABAS DO PERFIL")
        if r.status_code == 200 and r.json().get("items"):
            slug = r.json()["items"][0]["slug"]
            endpoints = [
                "candidacies", "assets", "campaign/revenues", "campaign/expenses",
                "election-results", "propositions", "votes", "attendance",
                "parliamentary-expenses", "news", "promises", "judicial-cases",
            ]
            for ep in endpoints:
                r3 = await client.get(f"/api/v1/politicians/{slug}/{ep}")
                if r3.status_code == 200:
                    body = r3.json()
                    items_count = len(body.get("data", body.get("items", [])))
                    report(f"  /{ep}", "OK", f"items={items_count}")
                else:
                    report(f"  /{ep}", "FAIL", f"status={r3.status_code}, err={r3.text[:100]}")

        # 7. Login
        print("\n[7] AUTENTICAÇÃO")
        r = await client.post("/api/v1/auth/login", json={
            "email": "douglassouza62@gmail.com",
            "password": "Dodo157359258789!"
        })
        if r.status_code == 200:
            token = r.json().get("access_token", "")[:20]
            report("POST /auth/login", "OK", f"token={token}...")

            # Test /users/me with token
            r4 = await client.get("/api/v1/users/me",
                                  cookies={"access_token": r.json()["access_token"]})
            if r4.status_code == 200:
                me = r4.json()
                report("GET /users/me", "OK", f"email={me.get('email')}, roles={me.get('roles')}")
            else:
                report("GET /users/me", "FAIL", f"status={r4.status_code}")
        else:
            report("POST /auth/login", "FAIL", f"status={r.status_code}, body={r.text[:200]}")

        # 8. Despesas parlamentares
        print("\n[8] DESPESAS IMPORTADAS")
        r8 = await client.get("/api/v1/politicians?limit=1")
        if r8.status_code == 200 and r8.json().get("items"):
            slug8 = r8.json()["items"][0]["slug"]
            r_exp = await client.get(f"/api/v1/politicians/{slug8}/parliamentary-expenses?limit=1")
            if r_exp.status_code == 200:
                exp_data = r_exp.json()
                exp_count = len(exp_data.get("data", []))
                total_amount = exp_data.get("aggregates", {}).get("total_net_amount", 0)
                report("Despesas via API", "OK" if exp_count > 0 else "WARN",
                       f"items={exp_count}, total=R${total_amount:,.2f}")
            else:
                report("Despesas via API", "FAIL", f"status={r_exp.status_code}")
        else:
            report("Despesas via API", "WARN", "Sem político para testar")

    # Summary
    print("\n" + "=" * 60)
    print("  RESUMO")
    print("=" * 60)
    ok = sum(1 for r in RESULTS if r["status"] == "OK")
    fail = sum(1 for r in RESULTS if r["status"] == "FAIL")
    warn = sum(1 for r in RESULTS if r["status"] == "WARN")
    print(f"\n  ✅ OK: {ok}  |  ❌ FAIL: {fail}  |  ⚠️ WARN: {warn}")
    print(f"  Total de testes: {len(RESULTS)}")

    if fail > 0:
        print("\n  FALHAS:")
        for r in RESULTS:
            if r["status"] == "FAIL":
                print(f"    ❌ {r['test']}: {r['detail']}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
