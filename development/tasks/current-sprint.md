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

  # Current Sprint — Task Tracking

- **Task ID:** TASK-002
- **Phase / Sprint:** Phase 1 / Sprint 1
- **Owner Role:** Builder
- **Goal:** Implement async document ingestion baseline.
- **Directives:**
  1. Set up File upload via FormData multipart.
  2. Implement BackgroundTasks worker placeholder in FastAPI.
- **Acceptance Criteria:**
  - [ ] Router accepts multi-part file payloads.
  - [ ] Server instantiates without errors or compiler warnings.
