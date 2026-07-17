# Knowledge — Environment

Reference for local environment configuration and service setup.

## Local Services

| Service | Image / Tool | Purpose | Port |
|---------|-------------|---------|------|
| PostgreSQL + pgvector | `pgvector/pgvector:pg17` | Primary datastore + vector similarity search | 5432 |
| Redis (optional) | `redis:7-alpine` | Caching / Celery broker | 6379 |
| MinIO (optional) | `minio/minio` | Local S3-compatible object storage for uploads | 9000/9001 |

### Quick Start (PowerShell)

```powershell
# Start Postgres (with pgvector) and Redis
docker compose up -d postgres redis

# Create and activate Python virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Run database migrations (Alembic)
alembic upgrade head

# Start FastAPI dev server
uvicorn app.main:app --reload --port 8000
```

## Environment Variables (`.env.local`, git-ignored)

| Variable | Purpose | Exposure |
|----------|---------|----------|
| `DATABASE_URL` | SQLAlchemy / asyncpg connection string | Backend only |
| `SECRET_KEY` | JWT signing / session encryption | Backend only |
| `OPENAI_API_KEY` | Embedding + chat model access | Backend only |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | Backend only |
| `FRONTEND_URL` | Used for OAuth redirects / email links | Backend only |
| `VITE_API_URL` | Backend base URL for the frontend | Frontend only |

## Rules
- Never hardcode secrets in code; keep them in `.env.local`.
- `.env.example` holds **placeholders only** (e.g. `DATABASE_URL=postgresql://user:pass@localhost:5432/sedap`).
- Remove transient tokens from `.env.local` after use.
- Use `python-decouple` or `pydantic-settings` to load env vars; never call `os.environ.get()` scattered across modules.
- Alembic migrations must target an explicit database URL (`-x url=...`) when running outside the default local container.
