# Deploy no EasyPanel — IFB

## Pré-requisitos

- Servidor com EasyPanel instalado
- Domínio configurado (DNS apontando para o servidor)
- GitHub repository configurado

## Passo a Passo

### 1. Criar Projeto no EasyPanel

1. Acesse o painel do EasyPanel
2. Crie um novo projeto: `ifb`
3. Configure o domínio base

### 2. Serviço: PostgreSQL

1. Adicionar serviço → Database → PostgreSQL
2. Nome: `ifb-postgres`
3. Versão: 16
4. Configurar credenciais (anotar para variáveis de ambiente)
5. Ativar volume persistente
6. Após criação, conectar e executar:
   ```sql
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   CREATE EXTENSION IF NOT EXISTS "pgcrypto";
   CREATE EXTENSION IF NOT EXISTS "vector";
   ```

### 3. Serviço: Redis

1. Adicionar serviço → Database → Redis
2. Nome: `ifb-redis`
3. Versão: 7
4. Ativar persistência

### 4. Serviço: MinIO

1. Adicionar serviço → Docker → MinIO
2. Nome: `ifb-minio`
3. Portas: 9000 (API), 9001 (Console)
4. Variáveis:
   - `MINIO_ROOT_USER`
   - `MINIO_ROOT_PASSWORD`
5. Criar bucket `ifb`

### 5. Serviço: Backend (API)

1. Adicionar serviço → Docker (GitHub)
2. Nome: `ifb-backend`
3. Build context: `./backend`
4. Dockerfile: `./backend/Dockerfile`
5. Porta: 8000
6. Domínio: `api.fiscalizabrasil.org.br`
7. HTTPS: Ativo (Let's Encrypt)
8. Variáveis de ambiente: todas do `.env.example`
9. Health check: `GET /api/v1/health`

### 6. Serviço: Worker

1. Adicionar serviço → Docker (GitHub)
2. Nome: `ifb-worker`
3. Build context: `./backend`
4. Dockerfile: `./backend/Dockerfile`
5. Comando: `celery -A app.workers.celery_app worker --loglevel=info --concurrency=4`
6. Sem porta exposta
7. Mesmas variáveis do backend

### 7. Serviço: Scheduler

1. Adicionar serviço → Docker (GitHub)
2. Nome: `ifb-scheduler`
3. Build context: `./backend`
4. Dockerfile: `./backend/Dockerfile`
5. Comando: `celery -A app.workers.celery_app beat --loglevel=info`
6. Sem porta exposta

### 8. Serviço: Frontend

1. Adicionar serviço → Docker (GitHub)
2. Nome: `ifb-frontend`
3. Build context: `./frontend`
4. Dockerfile: `./frontend/Dockerfile`
5. Porta: 3000
6. Domínio: `fiscalizabrasil.org.br` + `www.fiscalizabrasil.org.br`
7. HTTPS: Ativo
8. Variável: `NEXT_PUBLIC_API_URL=https://api.fiscalizabrasil.org.br`

### 9. Migrations

Após o backend subir, executar via terminal do EasyPanel:
```bash
alembic upgrade head
```

### 10. Backup Automático

Configurar no EasyPanel:
- PostgreSQL: backup diário às 03:00 UTC
- Retenção: 30 dias
- Storage: MinIO ou externo

## Monitoramento

- Health checks: ativos em todos os serviços
- Sentry: configurar `SENTRY_DSN`
- Prometheus + Grafana: adicionar como serviços opcionais

## Troubleshooting

### Backend não inicia
- Verificar logs no EasyPanel
- Confirmar que PostgreSQL e Redis estão healthy
- Verificar variáveis de ambiente

### Migrations falham
- Verificar conexão com o banco
- Confirmar que extensões foram criadas
- Rodar manualmente: `alembic upgrade head`

### Frontend 502
- Verificar se o backend está respondendo
- Confirmar CORS_ORIGINS inclui o domínio do frontend
