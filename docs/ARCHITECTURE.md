# Arquitetura — Instituto Fiscaliza Brasil (IFB)

## Visão Geral

O IFB é uma plataforma pública e apartidária que transforma dados públicos complexos em informações claras, rastreáveis e compreensíveis para qualquer cidadão.

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USUÁRIOS / NAVEGADOR                         │
└─────────────────────┬───────────────────────────────────────────────┘
                      │ HTTPS
┌─────────────────────▼───────────────────────────────────────────────┐
│                    PROXY REVERSO (EasyPanel/Nginx)                    │
│                    SSL Termination / Rate Limiting                    │
└──────┬──────────────────────────────────┬───────────────────────────┘
       │                                  │
┌──────▼──────────┐              ┌────────▼────────────────────────────┐
│   FRONTEND      │              │           BACKEND (FastAPI)          │
│   Next.js       │              │                                      │
│   Port: 3000    │              │   /api/v1/*                          │
│                 │              │   Auth / RBAC / Validação             │
│   - SSR/SSG    │              │   Rate Limiting / CORS                │
│   - React      │              │   Port: 8000                          │
│   - TypeScript  │              │                                      │
│   - Tailwind   │              └──┬───────────┬──────────┬────────────┘
└─────────────────┘                 │           │          │
                                    │           │          │
                    ┌───────────────▼─┐   ┌────▼────┐  ┌──▼──────────┐
                    │   PostgreSQL     │   │  Redis  │  │   MinIO     │
                    │   + pgvector     │   │         │  │   (S3)      │
                    │   Port: 5432     │   │  Cache  │  │             │
                    │                  │   │  Filas  │  │  Arquivos   │
                    │   Dados          │   │  Sessão │  │  Fotos      │
                    │   Auditoria      │   │         │  │  Docs       │
                    └──────────────────┘   └────┬────┘  └─────────────┘
                                                │
                                    ┌───────────▼───────────────────────┐
                                    │        CELERY WORKERS              │
                                    │                                    │
                                    │   - Sincronização de dados         │
                                    │   - Coleta de notícias             │
                                    │   - Classificação IA               │
                                    │   - Atualização de rankings        │
                                    │   - Processamento de webhooks      │
                                    │   - Envio de alertas               │
                                    └───────────────┬───────────────────┘
                                                    │
                                    ┌───────────────▼───────────────────┐
                                    │        CELERY BEAT (Scheduler)     │
                                    │                                    │
                                    │   - Cron jobs                      │
                                    │   - Agendamentos                   │
                                    │   - Sincronizações periódicas      │
                                    └───────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     INTEGRAÇÕES EXTERNAS                              │
│                                                                       │
│   TSE API │ Câmara API │ Senado API │ Portal Transparência           │
│   CGU │ TCU │ IBGE │ NewsAPI │ GDELT │ OpenAI │ Gateways Pagamento  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     OBSERVABILIDADE                                    │
│                                                                       │
│   Sentry │ Prometheus │ Grafana │ Loki │ Health Checks               │
└─────────────────────────────────────────────────────────────────────┘
```

## Princípios Arquiteturais

1. **Separação de responsabilidades**: Frontend e Backend são serviços independentes
2. **Segurança por design**: Autenticação e autorização exclusivamente no backend
3. **Rastreabilidade**: Todo dado possui fonte, data de coleta e método de obtenção
4. **Auditoria completa**: Todas as alterações são registradas com antes/depois
5. **Resiliência**: Circuit breakers, retries e filas para integrações externas
6. **Escalabilidade**: Workers independentes, cache distribuído, processamento assíncrono
7. **Transparência**: Metodologias públicas, fontes verificáveis, classificações explicáveis

## Padrões de Design

- **Repository Pattern**: Acesso a dados desacoplado da lógica de negócio
- **Service Layer**: Regras de negócio isoladas em serviços
- **Adapter Pattern**: Integrações externas abstraídas em adaptadores
- **Event-Driven**: Processamento assíncrono via filas (Celery/Redis)
- **CQRS Lite**: Separação de leitura/escrita em módulos críticos
- **Circuit Breaker**: Proteção contra falhas em APIs externas

## Estrutura de Diretórios

```
ifb-platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       ├── dependencies.py
│   │   │       └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── database.py
│   │   │   └── exceptions.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── integrations/
│   │   │   ├── tse/
│   │   │   ├── camara/
│   │   │   ├── senado/
│   │   │   ├── transparencia/
│   │   │   ├── cgu/
│   │   │   ├── tcu/
│   │   │   ├── ibge/
│   │   │   ├── news/
│   │   │   ├── judicial/
│   │   │   └── ai/
│   │   ├── workers/
│   │   ├── middleware/
│   │   └── main.py
│   ├── migrations/
│   ├── tests/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── services/
│   │   ├── types/
│   │   └── styles/
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├── infrastructure/
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── nginx/
│   └── easypanel/
├── docs/
├── scripts/
└── .env.example
```

## Modelo de Dados (Visão Simplificada)

```
users ──< user_roles >── roles ──< role_permissions >── permissions
  │
  ├── sessions
  ├── audit_logs
  └── user_favorites ──> politicians

politicians
  ├── politician_aliases
  ├── politician_social_links
  ├── party_memberships ──> parties
  ├── mandates
  ├── candidacies ──> elections
  │     ├── campaign_assets
  │     ├── campaign_revenues
  │     └── campaign_expenses
  ├── campaign_promises
  │     └── promise_evidences
  ├── legislative_projects
  ├── legislative_votes
  ├── legislative_attendance
  ├── parliamentary_expenses
  ├── public_amendments
  ├── lawsuits
  │     └── lawsuit_movements
  ├── news_mentions ──> news_articles
  │     └── news_classifications
  ├── ifb_scores
  │     └── score_components
  └── comparisons

news_articles ──> news_sources
ai_analysis_logs

donors ──< donations ──< donation_payments
payment_webhooks

transparency_revenues
transparency_expenses
institutional_documents

data_sources ──< data_sync_jobs ──< data_sync_logs
```

## Decisões Técnicas

| Decisão | Justificativa |
|---------|---------------|
| Python + FastAPI | Melhor ecossistema para IA, NLP e integrações com APIs públicas |
| Next.js + TypeScript | SSR para SEO, tipagem forte, excelente DX |
| PostgreSQL + pgvector | Banco robusto com suporte a busca semântica |
| Redis | Cache, filas Celery, sessões, rate limiting |
| Celery | Processamento assíncrono confiável com retry e monitoramento |
| Docker + EasyPanel | Deploy simplificado com isolamento de serviços |
| Argon2id | Algoritmo de hash recomendado para senhas (resistente a GPU) |
| JWT + Refresh Token | Autenticação stateless com rotação segura |

## Riscos Identificados

| Risco | Mitigação |
|-------|-----------|
| APIs externas instáveis | Circuit breakers, cache, retries, fallbacks |
| Custos com IA (OpenAI) | Rate limiting, cache de análises, batch processing |
| LGPD e dados sensíveis | Anonimização, consentimento, minimização |
| Ataques DDoS | Rate limiting, WAF, CloudFlare |
| Dados incorretos publicados | Revisão humana obrigatória para dados sensíveis |
| Acusação de viés político | Metodologia pública, fontes rastreáveis, apartidário |
