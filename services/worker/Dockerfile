FROM python:3.12-slim-bullseye

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn[standard] supabase-py python-dotenv redis celery

CMD ["celery", "-A", "worker", "worker", "-l", "info", "--concurrency=2"]