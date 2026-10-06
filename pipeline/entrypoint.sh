#!/bin/bash
# cron не наследует переменные окружения контейнера — сохраняем нужные в файл,
# который подгружается в crontab. %q экранирует спецсимволы в значениях.
for v in DATABASE_URL; do
    printf 'export %s=%q\n' "$v" "${!v}"
done > /app/.cron_env
chmod 600 /app/.cron_env

# Первый запуск сразу, не ждём начала часа (ошибка не должна ронять контейнер)
python /app/main.py || true

exec cron -f
