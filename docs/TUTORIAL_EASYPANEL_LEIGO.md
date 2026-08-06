# Tutorial Completo: Subir o IFB no EasyPanel (para leigos)

## O que você vai precisar

- Um servidor VPS com no mínimo 4GB RAM e 40GB de disco (recomendado: 8GB RAM)
- Um domínio apontando para o IP do servidor (ex: fiscalizabrasil.com.br)
- Acesso SSH ao servidor
- Conta no GitHub (para o EasyPanel clonar o repositório)

## Provedores recomendados de VPS

- Contabo (custo-benefício)
- Hetzner (performance)
- DigitalOcean (facilidade)
- Oracle Cloud (free tier com ARM)

Escolha um plano com Ubuntu 22.04 ou 24.04 LTS.

---

## PASSO 1: Instalar o EasyPanel no servidor

Conecte via SSH no seu servidor:

```bash
ssh root@SEU_IP
```

Instale o EasyPanel com um comando:

```bash
curl -sSL https://get.easypanel.io | sh
```

Aguarde a instalação (pode levar 2-5 minutos).

Ao terminar, acesse no navegador:

```
http://SEU_IP:3000
```

Crie sua conta de administrador do EasyPanel.

---

## PASSO 2: Apontar o domínio

No painel de DNS do seu domínio (Cloudflare, Registro.br, etc.), crie:

| Tipo | Nome | Valor |
|------|------|-------|
| A | @ | SEU_IP |
| A | www | SEU_IP |
| A | api | SEU_IP |

Aguarde propagação (pode levar até 24h, mas geralmente 5-30 min).

---

## PASSO 3: Criar o projeto no EasyPanel

1. No painel do EasyPanel, clique em **"Create Project"**
2. Nome: `ifb`
3. Clique em **"Create"**

---

## PASSO 4: Criar o banco PostgreSQL

1. Dentro do projeto `ifb`, clique **"+ Service"**
2. Escolha **"Postgres"**
3. Configure:
   - Nome: `postgres`
   - Versão: `16` (ou a mais recente disponível)
   - Database: `ifb`
   - Username: `ifb`
   - Password: anote uma senha forte (ex: `IFB_db_2026!seguro`)
4. Clique **"Create"**
5. Aguarde o container subir (status: Running)

**Importante:** Anote o hostname interno. Geralmente será:
```
postgres.ifb.internal
```

---

## PASSO 5: Criar o Redis

1. Clique **"+ Service"**
2. Escolha **"Redis"**
3. Configure:
   - Nome: `redis`
   - Versão: `7`
4. Clique **"Create"**

O hostname interno será:
```
redis.ifb.internal
```

---

## PASSO 6: Criar o MinIO (armazenamento de arquivos)

1. Clique **"+ Service"**
2. Escolha **"App"** → imagem Docker
3. Configure:
   - Nome: `minio`
   - Imagem: `minio/minio:latest`
   - Comando: `server /data --console-address :9001`
   - Porta principal: `9000`
   - Segunda porta: `9001` (para console)
   - Variáveis:
     - `MINIO_ROOT_USER` = `minioadmin`
     - `MINIO_ROOT_PASSWORD` = `MinIO_IFB_2026!`
   - Volume: Monte `/data` como volume persistente
4. Clique **"Create"**

---

## PASSO 7: Criar o Backend (API FastAPI)

1. Clique **"+ Service"**
2. Escolha **"App"** → GitHub
3. Configure:
   - Nome: `backend`
   - Repositório: `douglasoliveira21/ifb`
   - Branch: `main`
   - Build Path: `/backend`
   - Dockerfile: `Dockerfile`
   - Porta: `8000`

4. Na aba **"Environment"**, adicione TODAS estas variáveis:

```
APP_ENV=production
APP_NAME=Instituto Fiscaliza Brasil
APP_URL=https://api.fiscalizabrasil.com.br
FRONTEND_URL=https://fiscalizabrasil.com.br

POSTGRES_HOST=postgres.ifb.internal
POSTGRES_PORT=5432
POSTGRES_DB=ifb
POSTGRES_USER=ifb
POSTGRES_PASSWORD=IFB_db_2026!seguro

REDIS_URL=redis://redis.ifb.internal:6379/0

JWT_SECRET=GERE_UMA_STRING_ALEATORIA_DE_64_CARACTERES
JWT_ACCESS_EXPIRES_MINUTES=15
JWT_REFRESH_EXPIRES_DAYS=7

S3_ENDPOINT=http://minio.ifb.internal:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=MinIO_IFB_2026!
S3_BUCKET=ifb

SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@fiscalizabrasil.com.br

OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

CORS_ORIGINS=["https://fiscalizabrasil.com.br","https://www.fiscalizabrasil.com.br"]
```

5. Na aba **"Domains"**:
   - Adicione: `api.fiscalizabrasil.com.br`
   - Marque HTTPS (Let's Encrypt)

6. Na aba **"Health Check"**:
   - Path: `/api/v1/health`
   - Intervalo: 30s

7. Clique **"Deploy"**

---

## PASSO 8: Executar as migrations do banco

Após o backend estar rodando (status: Running):

1. No serviço `backend`, clique na aba **"Shell"** (ou Terminal)
2. Execute:

```bash
alembic upgrade head
```

Isso cria todas as 75 tabelas no PostgreSQL.

3. Em seguida, crie as roles e dados de referência:

```bash
python -m app.cli seed-roles
python -m app.cli seed-political-reference-data
```

4. Crie o superadministrador:

```bash
python -m app.cli create-superadmin
```

Siga as instruções (nome, e-mail, senha com mínimo 10 caracteres).

---

## PASSO 9: Criar o Worker Celery (processamento em background)

1. Clique **"+ Service"**
2. Escolha **"App"** → GitHub
3. Configure:
   - Nome: `worker`
   - Repositório: `douglasoliveira21/ifb`
   - Branch: `main`
   - Build Path: `/backend`
   - Dockerfile: `Dockerfile`
   - **Comando personalizado:**
     ```
     celery -A app.workers.celery_app worker -Q default,emails,tse,camara,senado,news-collect,news-ai,indicators,payments --loglevel=info --concurrency=4
     ```
   - Porta: **nenhuma** (não precisa expor porta)
   - Variáveis: **mesmas do backend** (copie todas)

4. Clique **"Deploy"**

---

## PASSO 10: Criar o Scheduler Celery (agendamentos)

1. Clique **"+ Service"**
2. Escolha **"App"** → GitHub
3. Configure:
   - Nome: `scheduler`
   - Repositório: `douglasoliveira21/ifb`
   - Branch: `main`
   - Build Path: `/backend`
   - Dockerfile: `Dockerfile`
   - **Comando personalizado:**
     ```
     celery -A app.workers.celery_app beat --loglevel=info
     ```
   - Porta: **nenhuma**
   - Variáveis: **mesmas do backend**

4. Clique **"Deploy"**

---

## PASSO 11: Criar o Frontend (Next.js)

1. Clique **"+ Service"**
2. Escolha **"App"** → GitHub
3. Configure:
   - Nome: `frontend`
   - Repositório: `douglasoliveira21/ifb`
   - Branch: `main`
   - Build Path: `/frontend`
   - Dockerfile: `Dockerfile`
   - Porta: `3000`

4. Na aba **"Environment"**:
```
NEXT_PUBLIC_API_URL=https://api.fiscalizabrasil.com.br
```

5. Na aba **"Domains"**:
   - Adicione: `fiscalizabrasil.com.br`
   - Adicione: `www.fiscalizabrasil.com.br`
   - Marque HTTPS

6. Clique **"Deploy"**

---

## PASSO 12: Verificar se tudo está funcionando

### Teste 1: Health check do backend
Abra no navegador:
```
https://api.fiscalizabrasil.com.br/api/v1/health
```

Deve retornar:
```json
{"status": "healthy", "version": "0.1.0", "environment": "production"}
```

### Teste 2: Documentação da API
Acesse (somente se APP_ENV não for "production"):
```
https://api.fiscalizabrasil.com.br/api/docs
```

### Teste 3: Frontend
Acesse:
```
https://fiscalizabrasil.com.br
```

Deve exibir a página inicial do IFB.

### Teste 4: Login
Acesse:
```
https://fiscalizabrasil.com.br/login
```

Use o e-mail e senha do superadmin criado no Passo 8.

---

## PASSO 13: Configurar backup automático

No terminal do serviço `postgres` do EasyPanel:

```bash
# Criar diretório de backup
mkdir -p /backups

# Testar backup manual
pg_dump -U ifb -d ifb --format=custom > /backups/ifb_manual.dump

# Verificar
pg_restore --list /backups/ifb_manual.dump
```

Para backup automático diário, use o recurso de backup do EasyPanel ou configure um cron no serviço.

---

## PASSO 14: Testar funcionalidades

### Criar um político de teste
Use o terminal do `backend`:
```bash
python -c "
import asyncio
from app.core.database import async_session_factory
from app.services.politician import PoliticianService
from app.services.audit import AuditService

async def test():
    async with async_session_factory() as db:
        audit = AuditService(db)
        service = PoliticianService(db, audit)
        p = await service.create(
            full_name='Político Teste da Silva',
            created_by='admin@ifb.org.br',
            ballot_name='TESTE SILVA',
            state_code='SP',
        )
        await service.publish(p.id, 'admin@ifb.org.br')
        await db.commit()
        print(f'Criado: {p.slug}')

asyncio.run(test())
"
```

Depois acesse:
```
https://fiscalizabrasil.com.br/politicos
```

---

## PASSO 15: Configurar domínio real (opcional)

Se estiver usando um domínio de teste, substitua `fiscalizabrasil.com.br` pelo seu domínio real em:
- Variáveis do backend (`APP_URL`, `FRONTEND_URL`, `CORS_ORIGINS`)
- Variáveis do frontend (`NEXT_PUBLIC_API_URL`)
- Configurações de domínio nos serviços do EasyPanel

---

## Resumo dos serviços criados

| Serviço | Tipo | Porta | Domínio |
|---------|------|-------|---------|
| postgres | PostgreSQL 16 | 5432 (interno) | — |
| redis | Redis 7 | 6379 (interno) | — |
| minio | MinIO | 9000/9001 (interno) | — |
| backend | FastAPI | 8000 | api.fiscalizabrasil.com.br |
| worker | Celery Worker | — | — |
| scheduler | Celery Beat | — | — |
| frontend | Next.js | 3000 | fiscalizabrasil.com.br |

---

## Troubleshooting

### Backend não inicia
- Verifique os logs no EasyPanel (aba "Logs" do serviço)
- Confirme que PostgreSQL e Redis estão "Running"
- Verifique as variáveis de ambiente (especialmente POSTGRES_PASSWORD)

### Migration falha
- Acesse o shell do backend
- Execute: `alembic current` para ver o estado
- Execute: `alembic upgrade head` novamente

### Frontend mostra erro
- Verifique se `NEXT_PUBLIC_API_URL` está correto
- Verifique se o backend está respondendo no domínio configurado
- Verifique CORS no backend

### Worker não processa
- Verifique se o Redis está acessível
- Verifique os logs do worker
- Confirme que REDIS_URL está correto

### Erro de CORS
- Adicione seu domínio em `CORS_ORIGINS` no backend
- Reinicie o backend após alterar

---

## Próximos passos após a instalação

1. **Configurar SMTP** para envio de e-mails (Mailgun, SendGrid, ou SMTP próprio)
2. **Configurar OpenAI** para classificação de notícias (opcional)
3. **Importar dados reais** do TSE usando a CLI
4. **Sincronizar** Câmara e Senado via admin
5. **Configurar gateway de pagamento** para doações

---

## Segurança importante

- **Troque TODAS as senhas padrão** antes de publicar
- **Gere um JWT_SECRET aleatório** (use: `openssl rand -base64 48`)
- **Não exponha** PostgreSQL, Redis ou MinIO publicamente
- **Ative HTTPS** em todos os domínios
- **Configure backup** antes de usar em produção
- **Ative MFA** para todas as contas administrativas

---

## Custo estimado

| Item | Custo mensal (estimativa) |
|------|--------------------------|
| VPS 8GB RAM | R$ 50–150 |
| Domínio .com.br | R$ 40/ano |
| SSL | Gratuito (Let's Encrypt) |
| EasyPanel | Gratuito (self-hosted) |
| **Total** | **~R$ 60–160/mês** |

---

*Tutorial criado para o Instituto Fiscaliza Brasil — Agosto 2026*
