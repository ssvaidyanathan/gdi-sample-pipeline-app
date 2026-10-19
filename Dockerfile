# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY app/ /app/app/

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

EXPOSE 8080

USER 1001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

# cache-warmup configuration asset for startup pre-warming
COPY config/cache-warmup.json /app/config/cache-warmup.json
