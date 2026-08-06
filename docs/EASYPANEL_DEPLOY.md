# Deploy EasyPanel — IFB (Configuração Operacional)

## Serviços

### 1. ifb-postgres
- **Imagem**: pgvector/pgvector:pg16
- **Volume**: /var/lib/postgresql/data (persistente)
- **Health**: `pg_isready -U ifb`
- **Backup**: diário às 03:00 UTC

### 2. ifb-redis
- **Imagem**: redis:7-alpine
- **Volume**: /data
- **Health**: `redis-cli ping`

### 3. ifb-minio
- **Imagem**: minio/minio
- **Volume**: /data
- **Portas**: 9000 (API), 9001 (Console)
- **Comando**: `server /data --console-address :9001`

### 4. ifb-backend
- **Build**: ./backend/Dockerfile
- **Porta**: 8000
- **Comando**: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`
- **Health**: GET /api/v1/health
- **Domínio**: api.fiscalizabrasil.org.br

### 5. ifb-worker-default
- **Build**: ./backend/Dockerfile
- **Comando**: `celery -A app.workers.celery_app worker -Q default,emails --loglevel=info --concurrency=2`
- **Sem porta exposta**

### 6. ifb-worker-tse
- **Build**: ./backend/Dockerfile
- **Comando**: `celery -A app.workers.celery_app worker -Q tse,imports --loglevel=info --concurrency=2`
- **Sem porta exposta**
- **Memória**: 1GB (arquivos grandes)

### 7. ifb-worker-camara
- **Build**: ./backend/Dockerfile
- **Comando**: `celery -A app.workers.celery_app worker -Q camara --loglevel=info --concurrency=2`
- **Sem porta exposta**

### 8. ifb-worker-senado
- **Build**: ./backend/Dockerfile
- **Comando**: `celery -A app.workers.celery_app worker -Q senado --loglevel=info --concurrency=2`
- **Sem porta exposta**

### 9. ifb-scheduler
- **Build**: ./backend/Dockerfile
- **Comando**: `celery -A app.workers.celery_app beat --loglevel=info`
- **Sem porta exposta**

### 10. ifb-frontend
- **Build**: ./frontend/Dockerfile
- **Porta**: 3000
- **Domínio**: fiscalizabrasil.org.br

## Filas Celery

| Fila | Workers | Uso |
|------|---------|-----|
| default | ifb-worker-default | Tarefas gerais |
| emails | ifb-worker-default | Envio de e-mail |
| tse | ifb-worker-tse | Importação TSE |
| imports | ifb-worker-tse | Importações genéricas |
| camara | ifb-worker-camara | Sync Câmara |
| senado | ifb-worker-senado | Sync Senado |

## Variáveis de Ambiente (Secrets)

Configurar no EasyPanel como secrets:
- `POSTGRES_PASSWORD`
- `JWT_SECRET`
- `OPENAI_API_KEY`
- `PAYMENT_API_KEY`
- `S3_ACCESS_KEY` / `S3_SECRET_KEY`
- `SMTP_PASSWORD`

## Migrations

Executar após deploy do backend:
```bash
# Via terminal EasyPanel do ifb-backend
alembic upgrade head
python -m app.cli seed-roles
python -m app.cli seed-political-reference-data
```

## Backups

### PostgreSQL
```bash
# Diário - configurar via cron no EasyPanel
pg_dump -U ifb -h localhost ifb | gzip > /backups/ifb_$(date +%Y%m%d).sql.gz
```

### MinIO
```bash
mc mirror minio/ifb /backups/minio/
```

## Health Checks

| Serviço | Endpoint | Intervalo |
|---------|----------|-----------|
| Backend | GET /api/v1/health | 30s |
| Frontend | GET / | 30s |
| PostgreSQL | pg_isready | 10s |
| Redis | redis-cli ping | 10s |
| MinIO | GET /minio/health/live | 30s |

## Restart Policy

Todos os serviços: `unless-stopped`

## Logs

- Sentry para erros de aplicação
- stdout/stderr capturados pelo EasyPanel
- Structured logging (JSON) em produção
