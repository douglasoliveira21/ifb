# Runbook de Sincronizações — IFB

## Cronograma automático (Celery Beat)

| Job | Horário | Fila | Dependência |
|-----|---------|------|-------------|
| Notícias | */2h | news-collect | Google News RSS |
| Proposições | 03:00 | camara | API Câmara |
| Despesas | 04:00 | camara | API Câmara |
| Senadores | 05:00 | senado | API Senado |

## Execução manual em lotes

### Deputados (proposições + comissões)
```bash
# 50 por vez, total ~513
python scripts/expand_all_deputies.py 50 0
python scripts/expand_all_deputies.py 50 50
# ... até 500
```
Tempo estimado: ~5 min por lote. Esperar 2 min entre lotes.

### Senadores (matérias + votações + comissões)
```bash
# 10 por vez, total ~81
python scripts/expand_all_senators.py 10 0
python scripts/expand_all_senators.py 10 10
# ... até 80
```
Tempo estimado: ~3 min por lote.

### Notícias em lote
```bash
# 50 políticos por vez
python scripts/collect_news_batch.py 50 0
python scripts/collect_news_batch.py 50 50
# ... até 594
```
Tempo estimado: ~3 min por lote (delay 2s entre políticos).

### Gastos parlamentares
```bash
python -m app.cli sync-expenses 2026
python -m app.cli sync-expenses 2025
```
Tempo estimado: ~20-30 min por ano (todos os deputados).

## Idempotência

Todos os scripts são idempotentes:
- Reprocessar o mesmo lote NÃO duplica dados
- Verificação por `external_id` + `house_id` antes de inserir
- Seguro para executar novamente após falha

## Monitoramento

### Dashboard rápido
```bash
python scripts/dashboard_ops.py
```

### Validação completa
```bash
python scripts/validate_rc1.py
```

## Limites conhecidos

| Fonte | Rate limit | Mitigação |
|-------|-----------|-----------|
| GDELT | ~1 req/s | Google News RSS como alternativa |
| Google News | ~1 req/2s | Delay 2s no script |
| Câmara | ~50 req/min | Delay 0.5s entre requests |
| Senado | ~30 req/min | Delay 1s entre requests |
| PostgreSQL | 100 conexões | Pool size limitado, esperar entre lotes |
| DeepSeek | Depende do plano | 3 classificações por político por execução |

## Erros comuns

| Erro | Causa | Solução |
|------|-------|---------|
| TooManyConnections | Pool esgotado | Esperar 2 min |
| 429 | Rate limit | Aumentar delay ou esperar |
| Timeout | API lenta | Retry automático |
| DataError datetime | String não parseada | Já corrigido no código |
