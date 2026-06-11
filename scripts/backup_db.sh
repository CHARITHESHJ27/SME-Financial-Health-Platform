#!/bin/sh
# scripts/backup_db.sh — runs daily inside the backup container
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
FILENAME="finexri_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup → $FILENAME"

PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
  -h "$POSTGRES_HOST" \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  --no-password \
  --clean \
  --if-exists | gzip > "$BACKUP_DIR/$FILENAME"

echo "[$(date)] Backup complete: $(du -sh $BACKUP_DIR/$FILENAME | cut -f1)"

# Keep only last 7 daily backups
find "$BACKUP_DIR" -name "finexri_*.sql.gz" -mtime +7 -delete
echo "[$(date)] Old backups pruned (keeping 7 days)"
