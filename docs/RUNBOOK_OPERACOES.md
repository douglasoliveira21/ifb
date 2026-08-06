# Runbook Operacional — IFB

## Sincronizações automáticas (Celery Beat)

| Job | Frequência | Fila |
|-----|-----------|------|
| Coleta de notícias | A cada 2h | news-collect |
| Proposições Câmara | Diário 3h | camara |
| Despesas Câmara | Diário 4h | camara |
| Senadores | Diário 5h | senado |

## Comandos manuais

### Expandir deputados
```bash
python scripts/expand_all_deputies.py 50 0
```

### Expandir senadores
```bash
python scripts/expand_all_senators.py 10 0
```

### Importar gastos
```bash
python -m app.cli sync-expenses 2026
```

### Coletar notícias (político específico)
```bash
python scripts/collect_news.py adriana-ventura --classify
```

### Coletar notícias em lote
```bash
python scripts/collect_news_batch.py 50 0
```

### Aprovar notícias pendentes
```bash
python -c "
import asyncio, sys; sys.path.insert(0, '/app')
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import get_settings
from app.models.news import NewsClassification
settings = get_settings()
async def run():
    engine = create_async_engine(settings.database_url, pool_size=2)
    factory = async_sessionmaker(engine, class_=AsyncSession)
    async with factory() as db:
        await db.execute(update(NewsClassification).where(NewsClassification.review_status == 'pending').values(review_status='approved'))
        await db.commit()
        print('Aprovadas')
    await engine.dispose()
asyncio.run(run())
"
```

## Monitoramento

### Health check
```bash
curl http://localhost:8000/api/v1/health
```

### Validação completa
```bash
python scripts/validate_rc1.py
```

### Validação legislativa
```bash
python scripts/validate_legislative.py
```

## Problemas comuns

### Too many connections
Esperar 2-3 minutos. Conexões expiram automaticamente.

### GDELT 429
O IP está bloqueado temporariamente. Usar Google News RSS como alternativa.

### Worker parado
Verificar logs no EasyPanel. Reiniciar serviço do worker.

## Backup
```bash
pg_dump -U ifb -d ifb --format=custom > /backups/ifb_$(date +%Y%m%d).dump
```
