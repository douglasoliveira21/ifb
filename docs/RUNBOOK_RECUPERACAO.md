# Runbook de Recuperação — IFB

## Banco de dados corrompido ou perdido

### Reconstruir do zero
```bash
alembic upgrade head
python -m app.cli seed-roles
python -m app.cli seed-political-reference-data
python -m app.cli create-superadmin
python -m app.cli import-deputies
python -m app.cli import-senators
python -m app.cli sync-expenses 2026
```

### Restaurar de backup
```bash
pg_restore -U ifb -d ifb --no-owner --clean /path/to/backup.dump
```

## Worker parado

1. Verificar logs no EasyPanel
2. Reiniciar serviço do worker
3. Verificar conexão com Redis
4. Verificar filas: `celery -A app.workers.celery_app inspect active`

## Redis indisponível

1. Reiniciar serviço Redis no EasyPanel
2. Rate limiting e sessions serão resetados
3. Não há perda de dados permanente

## API retornando 500

1. Verificar logs do backend
2. Problema mais comum: lazy loading (MissingGreenlet)
3. Verificar conexões PostgreSQL (too many clients)
4. Esperar 2 min e tentar novamente

## GDELT bloqueado (429)

1. Usar Google News RSS como alternativa (já configurado)
2. GDELT reseta em 1-2 horas
3. Não alterar configuração — o sistema usa Google News automaticamente

## Migração de servidor

1. No servidor novo: seguir tutorial EasyPanel
2. Executar sequência completa de reconstrução do banco
3. Validar com `python scripts/validate_rc1.py`
