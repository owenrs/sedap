# SEDAP — Coding Conventions & Non-Negotiable Constraints

Immutable coding laws, security rules, and architectural principles. Onboarding, workflow, agent contracts, and architecture live in their own files (see `onboarding.md` → Document Map).

## 1. Language & Framework Conventions

### Python (FastAPI Backend)
- **PEP 8 strict:** 4-space indentation, snake_case for functions/variables, PascalCase for classes, UPPER_SNAKE_CASE for constants.
- **Line length:** soft limit 88 characters (Black default); hard limit 99.
- **Imports:** sorted with `isort`; stdlib → third-party → local, blank line between groups.
- **Type hints:** required on all public function signatures and class attributes. Use `from __future__ import annotations` where needed to avoid forward-reference issues.
- **Docstrings:** Google or NumPy style on every public module, class, and function. Explain *why*, never state the obvious.
- **FastAPI patterns:** `async def` for all route handlers. Use `Annotated[Type, Depends()]` for dependency injection. Use `BackgroundTasks` for fire-and-forget work. Raise `HTTPException` with appropriate status codes; never return raw error dicts.

### TypeScript (SvelteKit / React Frontend)
- **TypeScript strict:** every file strictly typed; avoid `any`. Prefer `interface` over `type` for public contracts.
- **Folder structure:** components in `/components` (flat or logical groups);
- **Documentation:** JSDoc on every interface, public helper, and custom hook explaining *why*; never comment the obvious.

## 2. Async & Concurrency Patterns (FastAPI)
- **Never block the event loop.** Any blocking IO (sync DB driver, requests to external APIs, CPU-heavy work) must run in a thread pool via `anyio.to_thread.run_sync()` or `starlette.concurrency.run_in_threadpool()`.
- **Use async database drivers.** Prefer `asyncpg` (async) over `psycopg2` (sync) when using SQLAlchemy; use `SQLAlchemy 2.0` async sessions.
- **Background work:** long-running or non-critical tasks (emails, embeddings, file parsing) must use `BackgroundTasks` or a proper task queue (Celery / ARQ), never inline in the request handler.
- **Dependency injection:** keep `Depends()` callables lightweight; no heavy IO inside shared dependencies unless they are cached per-request.

## 3. Styling Conventions
- **Python:** enforced by `ruff` (lint) and `black` (format). No manual style tweaks.
- **TypeScript:** No custom CSS or inline styles unless strictly necessary.

## 4. Code Discipline Constraints
- **No Side-Effects:** do not modify files outside the current task's scope.
- **Verify, Don't Guess:** if a dependency or schema is unclear, pause and ask.
- **Keep Code Atomic:** one responsibility per file; split files beyond ~250 lines.
- **Token Conservation:** edit only changed blocks; explain *why* only when asked or when logic is complex.
- **Anti-Looping:** if a command/build fails twice with the same/similar error, STOP and escalate to the human with the error and the two distinct attempts. Never attempt a third automated fix.

## 5. Security & Environment Isolation
- **No hardcoded secrets** (keys, passwords, connection strings, JWTs) in code.
- Secrets/environment config live in `.env.local` (git-ignored); `.env.example` holds **placeholders only**.
- Python env loading must use `pydantic-settings` or `python-decouple`; never `os.environ.get()` scattered across modules.
- Never log `.env` values, request bodies containing secrets, or full stack traces to stdout in production.

## 6. Scalable Architectural Principles
Reactive symptoms, translated into forward-looking constraints so they never recur:

- **Single Source of Truth:** Infrastructure dependencies and API client initializations must have a single provider/singleton. All consumer files must import from this provider (e.g., `@/lib/supabase`). Never instantiate duplicate clients.
- **Strict Environment Isolation:** Secrets and configuration variables must reside in `.env.local` and be read strictly via environment abstractions. Never expose raw string keys in version-controlled code.
- **Explicit Environmental Scope:** Commands that execute database modifications or Docker operations must explicitly target specific connection strings or flags. Never rely on default system schemas or implicitly targeted database instances.
