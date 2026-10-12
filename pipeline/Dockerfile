FROM python:3.12-slim
# Unbuffered output so log lines reach `docker compose logs` immediately
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends cron && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
RUN crontab crontab && chmod +x entrypoint.sh
CMD ["/app/entrypoint.sh"]
