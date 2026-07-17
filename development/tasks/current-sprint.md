# Current Sprint — SEDAP Roadmap

> Mirrors `todo.md`. All phases complete as of the last integration into `dev`.

## Task 0: Project Initialization

---

## Task 1: Environment Baseline & Project Scaffolding

- **Task ID:** TASK-001
- **Phase / Sprint:** Phase 1 — Initialization
- **Owner Role:** Builder (with Architect sign-off on environment/dependency baseline)
- **Goal:** Establish a verified Python toolchain inside WSL and scaffold a minimal, runnable FastAPI project so the local server can be confirmed working before any feature work begins.
- **Directives:**
  1. Verify the `python3` and `pip` toolchain inside the WSL terminal (confirm versions and that `pip` resolves to the intended Python).
  2. Set up a Python virtual environment (`.venv`) in the project root and initialize a basic FastAPI application structure (project directory, dependency manifest, and entry module).
  3. Write a placeholder `main.py` endpoint (e.g., a health/root route) sufficient to verify the local server boots and responds.
- **Acceptance Criteria:**
  - [x] `python3 --version` and `pip --version` run successfully inside WSL and report compatible, expected versions.
  - [x] A `.venv/` virtual environment exists at the project root and is activated for subsequent work.
  - [x] A dependency manifest (`requirements.txt` or `pyproject.toml`) lists `fastapi` and an ASGI server (e.g., `uvicorn`).
  - [x] A placeholder `main.py` exposes at least one endpoint (root or `/health`) returning a 200 response.
  - [x] Running the local server (`uvicorn main:app`) starts cleanly and the placeholder endpoint returns a successful response (verified via curl/HTTP client).
  - [x] `tsc --noEmit` / `npm run lint` / `npm run build` gates are not applicable to this Python task; instead the server boot + endpoint check is the verification gate.
- **Notes / Risks:**
  - Confirm WSL distribution and that `python3` is the system/default interpreter, not a conda/shim wrapper.
  - `.venv/` must be git-ignored to avoid committing environment artifacts.
  - Do NOT implement application logic, ingestion, or embedding features yet — this task only establishes the baseline and confirms the server runs.
  - Pin dependency versions in the manifest to keep the environment reproducible (Architect to confirm pinning policy if needed).

---

## Task 2: Configuration Layer & Multi-Environment Baseline

- **Task ID:** TASK-002
- **Phase / Sprint:** Phase 1 — Initialization
- **Owner Role:** Builder (Architect sign-off on settings schema)
- **Goal:** Establish a type-safe settings engine using `pydantic-settings` that
  loads and strictly validates environment variables (DB credentials, app mode,
  secrets) from `.env`/`.env.local` with no hardcoded keys.
- **Directives:**
  1. Add `pydantic-settings` (and `pydantic`) to the dependency manifest and pin versions.
  2. Define a `Settings` model that parses required environment variables — at
     minimum `DATABASE_URL`, `SECRET_KEY`, and an app mode (e.g., `APP_ENV` ∈
     {dev, test, prod}) — via `pydantic-settings` `BaseSettings`, not scattered
     `os.environ.get()` (per `knowledge/environment.md` rules).
  3. Provide an `.env.example` with placeholders only (no real secrets), and
     ensure `.env` / `.env.local` stay git-ignored.
  4. Wire the settings module so `main.py` imports and instantiates it at
     startup, surfacing a clear failure if required vars are missing.
- **Acceptance Criteria:**
  - [x] `pydantic-settings` is added to `requirements.txt` and pinned.
  - [x] A `Settings` (or `AppConfig`) model exists loading env vars via
       `BaseSettings`, with required fields `DATABASE_URL`, `SECRET_KEY`, and
       `APP_ENV` strictly validated (types + allowed values).
  - [x] No secrets or credentials are hardcoded anywhere in source; all values
       resolve from the environment.
  - [x] `.env.example` exists with placeholder-only values; `.env` / `.env.local`
       are git-ignored.
  - [x] Loading valid env vars instantiates settings without error; omitting a
       required var raises a validation error at import/instantiation (no silent
       fallback).
  - [x] Linting and formatting checks pass (`ruff check .` or `flake8`).
  - [x] Type checks pass (`mypy .` if using strict type annotations).
  - [x] Server instantiates without errors or compiler warnings.
- **Notes / Risks:**
  - `knowledge/environment.md` already mandates `pydantic-settings` over
    `os.environ.get()` — honor that rule; do not scatter env reads.
  - Decide where the settings module lives (e.g., `app/core/config.py`) —
    coordinate with the eventual `app/` layout referenced in `environment.md`
    Quick Start (`uvicorn app.main:app`); keep this task decoupled from DB logic.
  - `SECRET_KEY` must be required (no default) to avoid insecure dev footguns;
    `APP_ENV` default may be `dev` but document the choice.
  - Do NOT implement database connections or ORM models here — only the
    config/validation surface.

---

## Task 3: Establish Code Quality Gates (Ruff & Mypy)

- **Task ID:** TASK-003
- **Phase / Sprint:** Phase 1 — Initialization
- **Owner Role:** Builder
- **Goal:** Introduce `ruff` and `mypy` as explicit project quality gates via a
  central root `pyproject.toml`, and make the existing `app/` codebase pass both
  with zero errors.
- **Directives:**
  1. Create `requirements-dev.txt` at the project root pinning the latest stable
     `ruff` and `mypy`.
  2. Create a root `pyproject.toml` configuring both tools: mypy `strict = true`;
     ruff select `F, E, W, I, B` (plus `format` config).
  3. Update `development/knowledge/environment.md` Quick Start to install both
     `requirements.txt` and `requirements-dev.txt`.
  4. Run `ruff check .`, `ruff format .`, and `mypy .`; fix any style/type
     divergence until both exit with 0 errors.
- **Acceptance Criteria:**
  - [x] `requirements-dev.txt` exists with pinned `ruff` and `mypy` versions.
  - [x] Root `pyproject.toml` exists with valid config for both tools.
  - [x] `ruff check .` returns clean (zero errors).
  - [x] `mypy app/` returns successfully (zero type errors).
  - [x] `environment.md` Quick Start lists dev dependency setup accurately.
  - [x] Sprint tracking updated locally; feature branch pushed to origin.
- **Notes / Risks:**
  - mypy `strict = true` is aggressive; the current `app/` code is small, so fix
    any strictness findings (e.g., implicit `Any`, missing return types) before
    reporting done.
  - Keep `requirements-dev.txt` separate from runtime `requirements.txt` so prod
    installs stay lean.
  - Do NOT alter runtime behavior/config schema; this task is tooling only.

---

## Task 4: Async Ingestion Pipeline Scaffolding

- **Task ID:** TASK-004
- **Phase / Sprint:** Phase 1 — Initialization
- **Owner Role:** Builder
- **Goal:** Establish a non-blocking, asynchronous file-ingestion pipeline using a
  clean in-memory queue (`asyncio.Queue` + background worker loop), abstracted
  behind a `Queue` interface so an `arq`/Redis provider can drop in later with
  zero route changes. No external Redis required.
- **Directives:**
  1. Define a queue interface/base in `app/core/queue.py` with `enqueue_job`
     and `get_job_status`; `settings` controls queue config.
  2. Implement `InMemoryQueue` using `asyncio.Queue` + a managed background
     worker loop (run-to-completion tasks).
  3. Define strict Pydantic job-status models (`job_id`, `status` ∈
     {pending, processing, completed, failed}, `created_at`, `result`).
  4. POST `/api/v1/ingest` accepts PDF/TXT/MD upload, enqueues a mock job
     immediately, returns `202 Accepted` with `job_id` (never blocks).
  5. GET `/api/v1/tasks/{job_id}` returns current job state/result.
  6. Mock extraction in the worker (async sleep ~3s, then return mock
     "Extracted text content" payload + metadata).
- **Acceptance Criteria:**
  - [x] No external Redis server required to boot or run the app.
  - [x] POST `/api/v1/ingest` accepts uploads and returns `202 Accepted` with a unique job ID.
  - [x] HTTP response returned immediately (< 50ms); file processed in background.
  - [x] GET `/api/v1/tasks/{job_id}` tracks transitions (pending → processing → completed) when polled during the mock window.
  - [x] Quality gates: `ruff check .` and `mypy app/` return 0 errors.
  - [x] `current-sprint.md` updated; changes committed cleanly to the local feature branch.
- **Notes / Risks:**
  - In-memory queue is process-local and non-durable — acceptable for baseline;
    the `Queue` interface isolates this so a Redis/`arq` backend swaps in later
    without touching routes (per operator directive).
  - Worker loop must be started with the app lifecycle (e.g., on FastAPI startup)
    so jobs run without a separate process for this baseline.
  - Keep `settings` the single source of queue config (e.g., mock processing
    delay / provider selection); no hardcoded tuning constants in routes.


