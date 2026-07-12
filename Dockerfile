FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY ballotsense_api /app/ballotsense_api

RUN pip install --no-cache-dir .

ENV PORT=8080

CMD ["sh", "-c", "uvicorn ballotsense_api.main:app --host 0.0.0.0 --port ${PORT}"]
