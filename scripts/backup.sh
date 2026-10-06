#!/bin/bash
# Daily PostgreSQL dump to S3. Run from cron on the server.
# cron has no variables from .env, so load them here.
set -euo pipefail

cd "$(dirname "$0")/.."
set -a; source .env; set +a

docker exec postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
  | gzip \
  | aws s3 cp - "s3://${BACKUP_BUCKET}/backup-$(date +%Y%m%d).sql.gz"
