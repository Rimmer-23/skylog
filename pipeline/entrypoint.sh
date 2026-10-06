#!/bin/bash
# cron does not inherit the container's environment, so save the needed variables to a file
# that the crontab sources. %q escapes special characters in values.
for v in DATABASE_URL; do
    printf 'export %s=%q\n' "$v" "${!v}"
done > /app/.cron_env
chmod 600 /app/.cron_env

# Run once immediately instead of waiting for the top of the hour (a failure must not kill the container)
python /app/main.py || true

exec cron -f
