#!/bin/bash
# Create (or refresh) the read-only PostgreSQL role used by Grafana.
# Idempotent: safe to run on every deploy. init.sql only runs on a fresh volume,
# so this script is what brings existing databases up to date.
set -euo pipefail

cd "$(dirname "$0")/.."
set -a; source .env; set +a
: "${GRAFANA_DB_PASSWORD:?GRAFANA_DB_PASSWORD must be set in .env}"

docker exec -i postgres psql -v ON_ERROR_STOP=1 -q \
    -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -v pw="$GRAFANA_DB_PASSWORD" -v db="$POSTGRES_DB" <<'SQL'
SELECT format('CREATE ROLE grafana_ro LOGIN PASSWORD %L', :'pw')
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'grafana_ro') \gexec

SELECT format('ALTER ROLE grafana_ro PASSWORD %L', :'pw') \gexec

ALTER ROLE grafana_ro SET default_transaction_read_only = on;

GRANT CONNECT ON DATABASE :"db" TO grafana_ro;

-- Dashboards read the curated layers
GRANT USAGE ON SCHEMA silver, gold TO grafana_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA silver, gold TO grafana_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA silver, gold GRANT SELECT ON TABLES TO grafana_ro;

-- Alerts only need run timestamps from bronze, not the raw payloads
GRANT USAGE ON SCHEMA bronze TO grafana_ro;
GRANT SELECT (id, fetched_at, location) ON bronze.weather_raw TO grafana_ro;
SQL

echo "grafana_ro is ready"
