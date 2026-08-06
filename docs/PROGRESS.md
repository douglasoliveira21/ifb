# Progresso IFB

## Fase atual

Fase 12 — Produção (preparação)

## Progresso geral

80%

## Todas as fases

| # | Fase | Status | Tabelas | Endpoints |
|---|------|--------|---------|-----------|
| 0 | Planejamento | ✅ | — | — |
| 1 | Fundação | ✅ | — | 2 |
| 2 | Autenticação | ✅ | 8 | 27 |
| 3 | Políticos | ✅ | 8 | 18 |
| 4 | TSE | ✅ | 9 | 5 |
| 5 | Legislativo | ✅ | 13 | 16 |
| 6 | Notícias/IA | ✅ | 7 | 7 |
| 7 | Promessas | ✅ | 6 | 8 |
| 8 | Judicial | ✅ | 7 | 4 |
| 9 | Indicadores | ✅ | 5 | 8 |
| 10 | Doações | ✅ | 7 | 9 |
| 11 | Transparência | ✅ | 5 | 6 |
| 12 | Produção | 🔄 | — | — |
| **Total** | | | **75** | **110+** |

## Migrations

| # | Nome | Tabelas |
|---|------|---------|
| 001 | Auth | 8 |
| 002 | Politicians | 8 |
| 003 | Elections/TSE | 9 |
| 004 | Legislative | 13 |
| 005 | News/AI | 7 |
| 006 | Promises | 6 |
| 007 | Judicial | 7 |
| 008 | Indicators | 5 |
| 009 | Donations/Transparency | 12 |
| **Total** | | **75 tabelas** |

## Pendências para produção

- [ ] Frontend integrado em todas as abas (hooks prontos)
- [ ] Testes E2E com Playwright
- [ ] Gateway de pagamento em sandbox real
- [ ] Validação EasyPanel com todos os workers
- [ ] Backup/restore testado
- [ ] Testes de carga (k6)
- [ ] Revisão de segurança (OWASP)
- [ ] CI/CD pipeline completo
- [ ] Grupo piloto validado

## Decisões técnicas consolidadas

- 75 tabelas PostgreSQL com constraints e índices
- 110+ endpoints REST com RBAC
- 9 migrations versionadas e encadeadas
- Celery com 10+ filas especializadas
- 30+ Celery tasks registradas
- Frontend: 18+ hooks TanStack Query
- IA: prompt com proteção contra injection
- Judicial: presunção de inocência como regra de sistema
- Indicadores: sem nota geral, dimensões independentes
- Doações: idempotência, webhook com assinatura, recibo
- Transparência: o IFB aplica a si mesmo o que cobra
- Backup: pg_dump custom com verificação e retenção 30d
