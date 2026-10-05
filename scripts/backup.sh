#!/bin/bash
# Ежедневный дамп PostgreSQL в S3. Запускается из cron на сервере.
# В cron нет переменных из .env, поэтому подгружаем их сами.
set -euo pipefail

cd "$(dirname "$0")/.."
set -a; source .env; set +a

docker exec postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
  | gzip \
  | aws s3 cp - "s3://${BACKUP_BUCKET}/backup-$(date +%Y%m%d).sql.gz"
