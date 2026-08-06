# API Reference — IFB

## Base URL

```
/api/v1
```

## Autenticação

Todas as rotas protegidas requerem JWT válido via cookie HttpOnly.
A documentação interativa está disponível em `/api/docs` (apenas em desenvolvimento).

## Rotas Implementadas (Fase 1)

### Health Check

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Status básico da aplicação |
| GET | `/health/detailed` | Status com verificação de PostgreSQL e Redis |

#### GET /health
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

#### GET /health/detailed
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "database": "healthy",
  "redis": "healthy"
}
```

## Rotas Planejadas (Fases 2+)

### Autenticação
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/auth/register` | Cadastro de novo usuário |
| POST | `/auth/login` | Login |
| POST | `/auth/refresh` | Renovar token |
| POST | `/auth/logout` | Logout |
| POST | `/auth/forgot-password` | Solicitar reset de senha |
| POST | `/auth/reset-password` | Resetar senha |
| POST | `/auth/verify-email` | Verificar e-mail |
| GET | `/auth/sessions` | Listar sessões |
| DELETE | `/auth/sessions/{id}` | Revogar sessão |

### Políticos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/politicians` | Listar/pesquisar políticos |
| GET | `/politicians/{id}` | Perfil completo |
| GET | `/politicians/{id}/summary` | Resumo com indicadores |
| GET | `/politicians/{id}/timeline` | Linha do tempo |
| GET | `/politicians/{id}/promises` | Promessas de campanha |
| GET | `/politicians/{id}/expenses` | Gastos públicos |
| GET | `/politicians/{id}/lawsuits` | Processos judiciais |
| GET | `/politicians/{id}/news` | Notícias relacionadas |
| GET | `/politicians/{id}/score` | Score IFB |

### Ranking
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/rankings` | Ranking geral |
| GET | `/rankings/methodology` | Metodologia |

### Doações
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/donations` | Iniciar doação |
| POST | `/donations/pix` | Gerar QR code PIX |
| POST | `/donations/webhooks/{provider}` | Webhook de pagamento |

*(Documentação completa será expandida a cada fase)*

## Códigos de Erro

| Código | Significado |
|--------|-------------|
| 400 | Requisição inválida |
| 401 | Não autenticado |
| 403 | Sem permissão |
| 404 | Recurso não encontrado |
| 409 | Conflito |
| 422 | Dados inválidos |
| 429 | Rate limit excedido |
| 500 | Erro interno |
| 502 | Serviço externo indisponível |

## Formato de Erro

```json
{
  "detail": "Mensagem descritiva do erro"
}
```
