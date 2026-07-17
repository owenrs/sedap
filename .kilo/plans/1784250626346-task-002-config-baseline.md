# Plan: TASK-002 — Configuration Layer & Multi-Environment Baseline

## Context
TASK-001 (environment baseline + runnable FastAPI placeholder) is complete on
`feature/TASK-001-env-scaffolding`; `todo.md` Phase 1 milestone line 5
("Configuration layer & Multi-environment baseline (.env)") is the next target.
`development/knowledge/environment.md` already mandates `pydantic-settings` for
env loading and lists the canonical variables (`DATABASE_URL`, `SECRET_KEY`,
`OPENAI_API_KEY`, `CORS_ORIGINS`, `FRONTEND_URL`, `VITE_API_URL`). This plan
scaffolds the sprint task only — no application/DB code is written yet.

## Goal
Establish a type-safe settings engine using `pydantic-settings` that loads and
strictly validates environment variables (DB credentials, app mode, secrets)
from `.env`/`.env.local`, with no hardcoded keys.

## Proposed Sprint Entry (append to `development/tasks/current-sprint.md`)

```markdown
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
  - [ ] `pydantic-settings` is added to `requirements.txt` and pinned.
  - [ ] A `Settings` (or `AppConfig`) model exists loading env vars via
       `BaseSettings`, with required fields `DATABASE_URL`, `SECRET_KEY`, and
       `APP_ENV` strictly validated (types + allowed values).
  - [ ] No secrets or credentials are hardcoded anywhere in source; all values
       resolve from the environment.
  - [ ] `.env.example` exists with placeholder-only values; `.env` / `.env.local`
       are git-ignored.
  - [ ] Loading valid env vars instantiates settings without error; omitting a
       required var raises a validation error at import/instantiation (no silent
       fallback).
  - [ ] Linting and formatting checks pass (`ruff check .` or `flake8`).
  - [ ] Type checks pass (`mypy .` if using strict type annotations).
  - [ ] Server instantiates without errors or compiler warnings.
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
```

## Open Decisions (need operator/Architect sign-off)
1. **Module location:** `app/core/config.py` (matches future `app.main:app`
   layout) vs root `config.py`. Recommend `app/core/config.py` to align with the
   `environment.md` Quick Start.
2. **`APP_ENV` default:** allow default `dev`, or require it explicitly?
   Recommend `dev` default with documented rationale.
3. **Scope of fields:** start with the 3 required core fields
   (`DATABASE_URL`, `SECRET_KEY`, `APP_ENV`) and optionally include the other
   `environment.md` variables now, or defer them. Recommend including the full
   set from `environment.md` to avoid churn.

## Execution Steps (for implementation-capable agent, after approval)
1. Create feature branch `feature/TASK-002-config-baseline` off `dev`.
2. Add `pydantic-settings==<pinned>` + `pydantic==<pinned>` to `requirements.txt`.
3. Create settings module (proposed `app/core/config.py`) with `BaseSettings`.
4. Add `.env.example` (placeholders only); confirm `.env*` git-ignored.
5. Import/instantiate settings in `main.py` startup.
6. Verify: valid env → clean boot; missing required var → validation error.
7. Run `ruff check .` / `mypy .` (if configured); mark sprint criteria `[x]`.
8. Commit locally; halt — operator pushes/merges.

## Validation
- `uvicorn` boots with a complete `.env`; fails fast with a clear error when a
  required variable is absent.
- `git status` shows no `.env` / `.env.local` tracked.

## Risks
- Editing `current-sprint.md` was blocked by the active permission rule
  (`edit` denied except plan files). Apply this plan via an agent with edit
  rights, or relax the rule, then commit on the feature branch.
