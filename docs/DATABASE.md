# Modelo de Banco de Dados — IFB

## Visão Geral

PostgreSQL 16 com extensão pgvector para busca semântica.

## Convenções

- Todos os IDs são UUID v4
- Timestamps com timezone (UTC)
- Soft delete via `deleted_at`
- Versionamento em tabelas críticas
- Campos de auditoria: `created_at`, `updated_at`, `created_by`, `updated_by`
- Campos de rastreabilidade: `source_id`, `source_url`, `collected_at`, `validated_at`

## Entidades por Módulo

### Core (Fase 1)
- `users` — Usuários da plataforma
- `roles` — Perfis de acesso (RBAC)
- `permissions` — Permissões granulares
- `role_permissions` — Associação role↔permission
- `user_roles` — Associação user↔role
- `sessions` — Sessões ativas (refresh tokens)
- `audit_logs` — Log de auditoria completo

### Políticos (Fase 3)
- `politicians` — Cadastro central de políticos
- `politician_aliases` — Nomes alternativos/urna
- `politician_social_links` — Redes sociais
- `parties` — Partidos políticos
- `party_memberships` — Histórico de filiações
- `mandates` — Mandatos exercidos

### Eleitoral (Fase 4)
- `elections` — Eleições (ano, turno, tipo)
- `candidacies` — Candidaturas
- `campaign_assets` — Patrimônio declarado
- `campaign_revenues` — Receitas de campanha
- `campaign_expenses` — Despesas de campanha

### Promessas (Fase 7)
- `campaign_promises` — Promessas de campanha
- `promise_evidences` — Evidências de cumprimento

### Parlamentar (Fase 5)
- `legislative_projects` — Projetos de lei
- `legislative_votes` — Votações nominais
- `legislative_attendance` — Presenças/ausências
- `parliamentary_expenses` — Gastos parlamentares
- `public_amendments` — Emendas parlamentares

### Judicial (Fase 8)
- `lawsuits` — Processos judiciais
- `lawsuit_movements` — Movimentações processuais

### Notícias (Fase 6)
- `news_sources` — Fontes de notícia
- `news_articles` — Notícias coletadas
- `news_mentions` — Menções a políticos
- `news_classifications` — Classificações IA

### Inteligência Artificial (Fase 6)
- `ai_analysis_logs` — Log de análises da IA

### Ranking (Fase 9)
- `ifb_scores` — Pontuações calculadas
- `score_methodologies` — Metodologias de cálculo
- `score_components` — Componentes individuais do score

### Comparações
- `comparisons` — Comparações salvas
- `user_favorites` — Políticos favoritados

### Notificações
- `alerts` — Alertas configurados
- `notifications` — Notificações enviadas

### Doações (Fase 10)
- `donors` — Doadores
- `donations` — Doações realizadas
- `donation_payments` — Pagamentos processados
- `payment_webhooks` — Webhooks recebidos

### Transparência (Fase 11)
- `transparency_revenues` — Receitas do instituto
- `transparency_expenses` — Despesas do instituto
- `institutional_documents` — Documentos públicos

### Sistema
- `data_sources` — Fontes de dados cadastradas
- `data_sync_jobs` — Jobs de sincronização
- `data_sync_logs` — Logs de sincronização
- `api_keys` — Chaves de API
- `system_settings` — Configurações do sistema

## Índices Recomendados

- `users.email` (unique)
- `politicians.cpf_hash` (unique)
- `politicians.nome_urna`
- `audit_logs.created_at`
- `audit_logs.user_id`
- `audit_logs.resource_type, resource_id`
- `news_articles.data_publicacao`
- `news_articles.politico_id`
- `lawsuits.politician_id, situacao`
- `ifb_scores.politician_id, created_at`

## Extensões PostgreSQL

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";
```
