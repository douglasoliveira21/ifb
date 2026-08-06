#!/bin/bash
# =============================================================================
# Restore PostgreSQL — Instituto Fiscaliza Brasil
# USO: ./restore-postgres.sh /backups/postgres/ifb_20260805.dump
# =============================================================================

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Uso: $0 <arquivo_backup.dump>"
    echo "Backups disponíveis:"
    ls -la /backups/postgres/ifb_*.dump 2>/dev/null || echo "  Nenhum backup encontrado."
    exit 1
fi

BACKUP_FILE="$1"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-ifb}"
DB_USER="${POSTGRES_USER:-ifb}"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERRO: Arquivo não encontrado: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  ATENÇÃO: Este comando irá restaurar o banco '$DB_NAME'."
echo "   Todos os dados atuais serão substituídos."
echo "   Backup: $BACKUP_FILE"
echo ""
read -p "Continuar? (sim/não): " CONFIRM

if [ "$CONFIRM" != "sim" ]; then
    echo "Operação cancelada."
    exit 0
fi

echo "[$(date)] Iniciando restauração..."

# Drop and recreate database
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "
    SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME';
"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Restore
pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --no-owner "$BACKUP_FILE"

echo "[$(date)] Restauração concluída com sucesso."
echo "Verifique o sistema e execute as migrations se necessário:"
echo "  alembic upgrade head"
