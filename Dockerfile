# syntax=docker/dockerfile:1

# ---- Stage 1: builder ----
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_CACHE_DIR=/wheels

# Minimal build toolchain for any native extensions (e.g. cryptography, orjson).
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Resolve + build wheels into the local cache (network only happens here).
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip wheel --wheel-dir /wheels -r requirements.txt


# ---- Stage 2: runner ----
FROM python:3.11-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_CACHE_DIR=/wheels \
    APP_HOME=/home/appuser

# Create a low-privileged user/group (UID/GID 10001).
RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --no-create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

# Install compiled wheels only — no network, no PyPI index.
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Application source.
COPY app ./app
COPY pyproject.toml .

# Drop root privileges.
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
