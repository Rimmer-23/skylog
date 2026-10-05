FROM python:3.12-slim
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
RUN crontab crontab && chmod +x entrypoint.sh
CMD ["/app/entrypoint.sh"]
