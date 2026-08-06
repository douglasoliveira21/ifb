# Instituto Fiscaliza Brasil — IFB

Plataforma pública e apartidária que transforma dados públicos complexos em informações claras, rastreáveis e compreensíveis sobre políticos brasileiros.

## Visão Geral

O IFB reúne, processa, analisa e apresenta informações públicas sobre políticos, candidatos e agentes públicos brasileiros, incluindo:

- Perfil político e histórico eleitoral
- Promessas de campanha e percentual de cumprimento
- Atividade parlamentar (projetos, votações, presença)
- Gastos públicos (cota parlamentar, emendas)
- Processos judiciais (com contexto e status correto)
- Notícias com classificação automática (com indicação de uso de IA)
- Ranking IFB com metodologia pública
- Transparência institucional completa

## Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Celery |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Banco | PostgreSQL 16 + pgvector |
| Cache/Filas | Redis 7 |
| Storage | MinIO (S3 compatível) |
| IA | OpenAI API (classificação de notícias) |
| Infra | Docker, EasyPanel |
| Monitoramento | Sentry, Prometheus, Grafana |

## Início Rápido

### Pré-requisitos

- Docker e Docker Compose
- Node.js 20+ (para desenvolvimento frontend)
- Python 3.12+ (para desenvolvimento backend)
- Git

### 1. Clonar o repositório

```bash
git clone <repo-url> ifb-platform
cd ifb-platform
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas credenciais
```

### 3. Subir infraestrutura (Docker)

```bash
cd infrastructure
docker compose up -d postgres redis minio
```

### 4. Backend (desenvolvimento)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"

# Executar migration
alembic upgrade head

# Criar roles e permissões padrão
python -m app.cli seed-roles

# Criar superadministrador
python -m app.cli create-superadmin

# Rodar servidor de desenvolvimento
uvicorn app.main:app --reload --port 8000
```

### 5. Frontend (desenvolvimento)

```bash
cd frontend
npm install
npm run dev
```

### 6. Acessar

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1/health
- Docs API: http://localhost:8000/api/docs
- MinIO Console: http://localhost:9001

## Testes

### Backend
```bash
cd backend
pytest
pytest tests/test_security.py -v  # Testes de segurança
pytest tests/test_auth.py -v      # Testes de autenticação
pytest --cov=app --cov-report=term-missing  # Com cobertura
```

### Frontend
```bash
cd frontend
npm run lint
npm run type-check
```

## Estrutura do Projeto

```
ifb-platform/
├── backend/          # API FastAPI
├── frontend/         # Interface Next.js
├── infrastructure/   # Docker, EasyPanel configs
├── docs/             # Documentação completa
├── scripts/          # Scripts de manutenção
└── .env.example      # Template de variáveis
```

## Documentação

| Documento | Descrição |
|-----------|-----------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura e decisões técnicas |
| [DATABASE.md](docs/DATABASE.md) | Modelo de dados |
| [API.md](docs/API.md) | Referência da API |
| [SECURITY.md](docs/SECURITY.md) | Políticas de segurança |
| [DEPLOY_EASYPANEL.md](docs/DEPLOY_EASYPANEL.md) | Guia de deploy |
| [ROADMAP.md](docs/ROADMAP.md) | Roadmap de fases |
| [PROGRESS.md](docs/PROGRESS.md) | Progresso atual |

## Princípios

1. **Apartidário** — Não expressa opinião política
2. **Rastreável** — Toda informação tem fonte e data
3. **Transparente** — Metodologias públicas e explicáveis
4. **Responsável** — Nunca trata investigação como condenação
5. **Auditável** — Todas as alterações são registradas
6. **Seguro** — LGPD, criptografia, controle de acesso

## Licença

Este projeto é de código fonte próprio do Instituto Fiscaliza Brasil.
