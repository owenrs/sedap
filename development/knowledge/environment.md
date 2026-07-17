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

# Install runtime + dev dependencies (dev brings ruff + mypy)
pip install -r requirements.txt -r requirements-dev.txt

# Run database migrations (Alembic)
alembic upgrade head

# Start FastAPI dev server
uvicorn app.main:app --reload --port 8000
```

### Quality Gates (ruff + mypy)
Defined centrally in root `pyproject.toml` (mypy `strict = true`; ruff selects
`F, E, W, I, B`). Run inside the activated venv / WSL:

```powershell
# Lint + auto-format
ruff check .
ruff format .

# Static type checking (strict)
mypy app/
```

Both must exit 0 before committing. On WSL, create the venv from Linux
(`wsl -d Ubuntu -- python3 -m venv .venv`) so the tools bind the Linux
interpreter (see WSL pip bootstrap note below).

## Environment Variables (`.env.local`, git-ignored)

| Variable | Purpose | Exposure |
|----------|---------|----------|
| `DATABASE_URL` | SQLAlchemy / asyncpg connection string | Backend only |
| `SECRET_KEY` | JWT signing / session encryption | Backend only |
| `OPENAI_API_KEY` | Embedding + chat model access | Backend only |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | Backend only |
| `FRONTEND_URL` | Used for OAuth redirects / email links | Backend only |
| `VITE_API_URL` | Backend base URL for the frontend | Frontend only |

## WSL pip bootstrap (Ubuntu distro)
- The default WSL `Ubuntu` image ships Python 3.14.x **without** `pip` or `ensurepip` (`python3 -m pip` → `No module named pip`). Verify first with `wsl -d Ubuntu -- python3 -m pip --version`.
- If missing, bootstrap via `sudo apt-get install python3-pip python3-venv` (or `python3-full` for ensurepip). A stalled/empty `apt-get` output usually means no network egress from WSL — fix the mirror/network before retrying.
- Create the project venv from WSL so it binds the Linux interpreter: `wsl -d Ubuntu -- python3 -m venv /mnt/e/engineering/sedap/.venv`. Windows-side `python -m venv` produces a Windows venv that won't run under WSL.
- Run the server and curl from inside WSL (e.g. `wsl -d Ubuntu -- curl http://127.0.0.1:8000/health`); a WSL-spawned background server is killed when its shell exits, so keep it under a persistent background process.

## Rules
- Never hardcode secrets in code; keep them in `.env.local`.
- `.env.example` holds **placeholders only** (e.g. `DATABASE_URL=postgresql://user:pass@localhost:5432/sedap`).
- Remove transient tokens from `.env.local` after use.
- Use `python-decouple` or `pydantic-settings` to load env vars; never call `os.environ.get()` scattered across modules.
- Alembic migrations must target an explicit database URL (`-x url=...`) when running outside the default local container.
