#!/bin/bash
# =============================================================================
# Backup PostgreSQL — Instituto Fiscaliza Brasil
# Executar via cron diariamente no EasyPanel
# =============================================================================

set -euo pipefail

BACKUP_DIR="/backups/postgres"
RETENTION_DAYS=30
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-ifb}"
DB_USER="${POSTGRES_USER:-ifb}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/ifb_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "[$(date)] Starting PostgreSQL backup..."

pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  --format=custom --compress=6 \
  -f "${BACKUP_DIR}/ifb_${TIMESTAMP}.dump"

echo "[$(date)] Backup created: ifb_${TIMESTAMP}.dump"

# Remove old backups
find "${BACKUP_DIR}" -name "ifb_*.dump" -mtime +${RETENTION_DAYS} -delete
echo "[$(date)] Old backups cleaned (retention: ${RETENTION_DAYS} days)"

# Verify backup
pg_restore --list "${BACKUP_DIR}/ifb_${TIMESTAMP}.dump" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "[$(date)] Backup verification: OK"
else
    echo "[$(date)] WARNING: Backup verification failed!"
    exit 1
fi

echo "[$(date)] Backup completed successfully."
