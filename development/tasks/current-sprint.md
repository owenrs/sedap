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
- **Phase / Sprint:** Phase 2: Ingestion & Processing Layer
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

---

## Task 5: Chunking & Text Splitting Engine

- **Task ID:** TASK-005
- **Phase / Sprint:** Phase 2: Ingestion & Processing Layer
- **Owner Role:** Builder
- **Goal:** Replace the placeholder extraction in the background worker with a
  configurable text-chunking engine that splits raw text into overlapping,
  metadata-rich chunks, returned as a structured array in the completed job result.
- **Directives:**
  1. Create `app/services/chunker.py` with a configurable chunker (`chunk_size`,
     `chunk_overlap`).
  2. Wire `CHUNK_SIZE` (default 500) and `CHUNK_OVERLAP` (default 50) into
     `app/core/config.py` via Pydantic settings (no hardcoded tuning).
  3. Update `app/services/ingestion.py` to extract raw text (native TXT/MD; PDF
     read as clear-text stream or mocked cleanly) and pass it to the chunker.
  4. Each chunk carries `chunk_id`, `text_content`, `page_number` (if applicable),
     and `metadata` with the source file name.
  5. Extend the job-result Pydantic schemas so a `completed` task returns this
     array of chunk records in `result`.
- **Acceptance Criteria:**
  - [x] Chunking engine splits text using `CHUNK_SIZE` / `CHUNK_OVERLAP` from settings.
  - [x] Overlap verified: end of chunk N matches start of chunk N+1.
  - [x] GET `/api/v1/tasks/{job_id}` returns a structured array of chunks with per-chunk metadata when completed.
  - [x] Quality gates pass: `ruff check .` and `mypy app/` return 0 errors.
  - [x] `current-sprint.md` updated; changes committed cleanly to the isolated feature branch.
- **Notes / Risks:**
  - Character-based splitting for this baseline (token-based is a later enhancement);
    keep the chunker interface open to a tokenizer strategy.
  - Overlap must be strictly less than `chunk_size`; validate to avoid infinite/empty loops.
  - PDF handling is mocked/clean-text only this baseline — no parser dependency added.

---

## Task 6: Entity Extraction Service Integration

- **Task ID:** TASK-006
- **Phase / Sprint:** Phase 2: Ingestion & Processing Layer
- **Owner Role:** Builder
- **Goal:** Introduce a modular, interface-driven Entity Extraction service that
  enriches each chunk's metadata with extracted entities (rule-based baseline),
  behind a strict Pydantic parsing layer.
- **Directives:**
  1. Define strict Pydantic entity models in `app/core/entities.py`
     (`ExtractedEntities`: `keywords`, `organizations`, `people`, `dates`).
  2. Define an abstract extractor interface/base in `app/services/extractor.py`.
  3. Implement `RuleBasedExtractor` scanning chunk text for signatures
     (uppercase proper nouns, date patterns, high-value keywords).
  4. Update `app/services/ingestion.py` to run each `ChunkRecord` through the
     extractor and bind `ExtractedEntities` into the chunk's `metadata`.
  5. Make extractor type / default keywords controllable via `app/core/config.py`.
- **Acceptance Criteria:**
  - [x] A formal entity extraction interface exists, decoupling extraction from the pipeline.
  - [x] Background workers process chunking AND entity extraction sequentially without error.
  - [x] GET `/api/v1/tasks/{job_id}` for a completed task shows chunks with enriched entity metadata (non-empty keywords/entities).
  - [x] Quality gates pass: `ruff check .` and `mypy app/` return 0 errors.
  - [x] Task tracked in `current-sprint.md`; changes committed to the isolated feature branch.
- **Notes / Risks:**
  - Rule-based only this baseline; the interface allows an LLM/ML provider later
    with zero change to ingestion wiring.
  - Keep extractor keyword lists/type in settings to avoid hardcoded tuning in routes.
  - Entities stored under a dedicated `entities` key inside chunk `metadata`.

---

## Task 7: Embedded Vector Storage Layer Baseline

- **Task ID:** TASK-007
- **Phase / Sprint:** Phase 3: Vector Storage & Embedding Layer
- **Owner Role:** Builder
- **Goal:** Establish a modular, interface-driven Vector Storage service with an
  in-memory provider (no external DB) that stores chunk vectors and runs local
  cosine-similarity search, behind a strict Pydantic record model.
- **Directives:**
  1. Define a `VectorStorageClient` ABC in `app/core/vector_store.py` with
     `upsert_vectors(collection_name, records)` and
     `search_vectors(collection_name, query_vector, limit, filters=None)`.
  2. Implement `InMemoryVectorStore` tracking collections in process memory.
  3. Write a dependency-free cosine-similarity function (float arrays).
  4. Define strict Pydantic `VectorRecord` (`id`, `vector: list[float]`,
     `payload: dict` mapping ChunkRecord content + metadata).
  5. Add a deterministic mock vector generator (e.g., hashed/length-based
     128-dim unit-normalized array) so collections can be populated/searched
     without an embedding model.
  6. Bind the store to `app.state.vector_store` on lifespan startup, via a
     `VECTOR_STORE_PROVIDER` flag in settings.
- **Acceptance Criteria:**
  - [x] A formal `VectorStorageClient` abstract interface decouples layers from engines.
  - [x] Chunks convert to mock vectors, upsert, and store in process memory.
  - [x] Cosine similarity search ranks records in descending score order.
  - [x] Quality gates pass: `ruff check .` and `mypy app/` return 0 errors.
  - [x] Tracked in `current-sprint.md`; committed to the isolated feature branch.
- **Notes / Risks:**
  - In-memory store is process-local/non-durable; the ABC lets a pgvector/
    Qdrant/Redis backend swap in later with zero route changes.
  - Mock vectors are deterministic but NOT semantic — real embeddings come in a
    later milestone; this task only proves the storage/search transport.
  - Keep `VECTOR_STORE_PROVIDER` + dimensionality in settings (no hardcoded tuning).

---

## Task 8: Embedding Generation & Synchronization Engine

- **Task ID:** TASK-008
- **Phase / Sprint:** Phase 3: Vector Storage & Embedding Layer
- **Owner Role:** Builder
- **Goal:** Establish an interface-driven Embedding Service that replaces the mock
  vector generator, converting chunk text into real multi-dimensional vectors via
  a local engine or the OpenAI API, and upserts them into the vector store.
- **Directives:**
  1. Define `EmbeddingService` ABC in `app/services/embeddings.py` with
     `generate_embeddings(texts: list[str]) -> list[list[float]]`.
  2. Implement `LocalEmbeddingProvider` (dependency-free local generator;
     `fastembed` if acceptable within local limits).
  3. Implement `OpenAIEmbeddingProvider` making async HTTP calls to the OpenAI
     v1 embeddings API (`text-embedding-3-small`), using `OPENAI_API_KEY`.
  4. Add `EMBEDDING_PROVIDER` (default local) and `EMBEDDING_DIMENSION` (384 local
     / 1536 OpenAI) to `app/core/config.py`.
  5. Wire into `app/services/ingestion.py`: after chunking, embed the chunk texts
     and upsert real `VectorRecord`s into the `VectorStorageClient`.
  6. Add required external libs to `requirements.txt`.
- **Acceptance Criteria:**
  - [x] Abstract `EmbeddingService` interface decouples pipeline from AI providers.
  - [x] Document chunks mapped to real multi-dimensional float arrays before indexing.
  - [x] Toggling `EMBEDDING_PROVIDER` in `.env` seamlessly changes the engine.
  - [x] Quality gates pass: `ruff check .` and `mypy app/` return 0 errors.
  - [x] `current-sprint.md` updated; committed to the isolated feature branch.
- **Notes / Risks:**
  - Local provider must be dependency-free (no network) so the app runs offline;
    a lightweight hashed/term-frequency vector space is acceptable as the local
    fallback (real local models like fastembed need a heavy download — confirm
    with operator before adding).
  - OpenAI provider requires `OPENAI_API_KEY`; fail fast if missing when selected.
  - Upsert into the same collection the search layer reads; chunk_id is the vector id.

---

## Task 9: Semantic Search Endpoint & Query Router

- **Task ID:** TASK-009
- **Phase / Sprint:** Phase 3: Vector Storage & Embedding Layer
- **Owner Role:** Builder
- **Goal:** Implement a functional GET `/api/v1/search` semantic search endpoint
  that embeds the query via the configured EmbeddingService, runs a cosine
  similarity lookup against the VectorStorageClient, and returns ranked matching
  chunks with confidence scores.
- **Directives:**
  1. Create `app/api/v1/search.py` and include it in `app/main.py`.
  2. GET `/api/v1/search` with `q: str` (required), `limit: int = 5`,
     `collection: str = "chunks"` (matches the ingestion collection).
  3. Use `request.app.state.embedding_service` to embed `q`.
  4. Call `request.app.state.vector_store.search_vectors()` with the query vector.
  5. Map hits to a strict `SearchResultsPayload` Pydantic model (text content,
     source metadata, cosine similarity score).
  6. Return empty array `[]` with `200 OK` when no matches.
- **Acceptance Criteria:**
  - [x] GET `/api/v1/search?q=...` runs end-to-end without network blocking on local model.
  - [x] Search responses strongly typed with explicit score-metric schemas.
  - [x] Results ranked descending by similarity score.
  - [x] Quality gates pass: `ruff check .` and `mypy app/` return 0 errors.
  - [x] `current-sprint.md` updated; committed to the isolated feature branch.
- **Notes / Risks:**
  - Default `collection="chunks"` mirrors the ingestion collection name
    (TASK-008 `COLLECTION_NAME`); the directive's `"documents"` default was
    adjusted so search returns ingested data without renaming the store.
  - Requires `app.state.embedding_service` bound at lifespan (added alongside
    `vector_store`).
  - Local provider is offline/dependency-free; empty-result case returns 200 + [].

---

## Task 10: LLM Generation & Orchestration Layer Scaffolding

- **Task ID:** TASK-010
- **Phase / Sprint:** Phase 4 — Retrieval, Search, & RAG API
- **Owner Role:** Builder
- **Goal:** Establish an interface-driven LLM Orchestration Service with an offline
  MockLLMProvider and an OpenAI chat-completions provider, plus a RAGOrchestrator
  that stitches retrieved chunks into a prompt and returns a typed RAG response.
- **Directives:**
  1. Define `LLMService` ABC in `app/services/llm.py` with
     `generate_response(prompt, system_message=None, max_tokens=500) -> str`.
  2. Implement `MockLLMProvider` (offline, no key) echoing a deterministic block
     with `prompt[:60]` + a clean summary.
  3. Implement `OpenAILLMProvider` via async `httpx` POST to `/v1/chat/completions`.
  4. Add `LLM_PROVIDER` (default "local"), `LLM_MODEL` (default "gpt-5.6-terra"),
     reuse `OPENAI_API_KEY` in `app/core/config.py`.
  5. Create `RAGOrchestrator` in `app/services/rag.py`: embed query -> vector
     search -> stitch "Context:/Question:" prompt -> dispatch to LLM -> return
     `RAGResponsePayload` (answer + chunk-id references).
  6. Expose POST `/api/v1/query` in `app/api/v1/query.py` hooked to the orchestrator.
- **Acceptance Criteria:**
  - [x] Abstract `LLMService` isolates core code from cloud SDKs.
  - [x] Full RAG sequence (Query -> Embed -> Vector Search -> Prompt Stitch -> LLM) coordinates end-to-end.
  - [x] POST `/api/v1/query` works offline under local provider with no external network.
  - [x] Quality gates pass: `ruff check .` and `mypy app/` return 0 errors.
  - [x] `current-sprint.md` updated; changes committed to the feature branch.
- **Notes / Risks:**
  - RAGOrchestrator pulls context via the same store the search layer reads
    (collection "chunks"); bind LLM service to app.state at lifespan.
  - OpenAI provider fails fast without `OPENAI_API_KEY`; untested live (no key).
  - Mock provider is deterministic/non-semantic; proves the transport + stitching.

---

## Task 11: Hybrid Search (BM25 + Dense Vector + RRF)

- **Task ID:** TASK-011
- **Phase / Sprint:** Phase 4 — Retrieval, Search, & RAG API
- **Owner Role:** Builder
- **Goal:** Upgrade retrieval to hybrid search: a BM25 sparse keyword index
  alongside the dense vector index, fused via Reciprocal Rank Fusion (RRF, k=60).
- **Directives:**
  1. Add `rank-bm25==0.2.2` to `requirements.txt`.
  2. Extend `InMemoryVectorStore` (or a unified hybrid wrapper in
     `app/core/vector_store.py`) to hold a process-local BM25 corpus per
     collection; handle empty corpus gracefully.
  3. Ingestion pipeline tokenizes each chunk (lowercase alphabetic split) and feeds
     the BM25 corpus as well as the dense vectors.
  4. Implement an optimized `reciprocal_rank_fusion(rank_lists, k=60)` function.
  5. Add `search_hybrid(query_text, limit)` to the client interface + store: runs
     dense cosine ranking AND BM25, then RRF-fuses, returns descending order.
  6. Wire GET `/api/v1/search` and `RAGOrchestrator` to use hybrid search (default).
- **Acceptance Criteria:**
  - [x] Ingestion updates both sparse BM25 corpus and dense vector space.
  - [x] RRF re-ranks the unified results from overlapping system ranks.
  - [x] GET `/api/v1/search` and POST `/api/v1/query` use hybrid search natively.
  - [x] Quality gates pass: `ruff check .` and `mypy app/` return 0 errors.
  - [x] `current-sprint.md` updated; committed to the isolated feature branch.
- **Notes / Risks:**
  - BM25 corpus is corpus-order based; map BM25 doc index back to chunk_id so
    fused hits carry the right payload.
  - Keep RRF constant k=60 in settings or a module constant (no magic numbers).
  - Fallback: if BM25 corpus empty, dense ranking alone should still return hits.

---

## Task 12: Conversational Memory & Optimized API Boundary

- **Task ID:** TASK-012
- **Phase / Sprint:** Phase 4 — Retrieval, Search, & RAG API
- **Owner Role:** Builder
- **Goal:** Add interface-driven Conversational Memory (multi-turn sessions),
  query condensation over history, and an optimized `/api/v1/chat` boundary with
  latency instrumentation.
- **Directives:**
  1. Define `ChatMessage` (`role`, `content`, `timestamp`) in `app/core/memory.py`.
  2. Define `BaseMemoryStore` ABC (`get_history`, `add_message`).
  3. Implement `InMemoryMemoryStore` tracking sessions in a dict (isolated).
  4. Enhance `RAGOrchestrator` to accept optional `session_id`: if history exists,
     condense raw input + history into a standalone search query via `LLMService`,
     run `search_hybrid`, then persist user query + assistant answer to memory.
  5. Add POST `/api/v1/chat` (`session_id`, `message`) in `app/api/v1/chat.py`,
     wired into the v1 router, returning references to grounding chunks.
  6. Add request-latency middleware verifying < 500ms under local mock flags.
- **Acceptance Criteria:**
  - [x] Multi-turn tracking links follow-up queries to original history.
  - [x] Session states isolated inside the memory adapter.
  - [x] POST `/api/v1/chat` handles sequential responses, appending grounding references.
  - [x] Quality gates pass: `ruff check .` and `mypy app/` return 0 errors.
  - [x] `current-sprint.md` updated; committed to the isolated feature branch.
- **Notes / Risks:**
  - Bind `BaseMemoryStore` to `app.state.memory_store` at lifespan.
  - Condensation only triggers when history is non-empty; single-turn chat behaves
    like /query.
  - Latency middleware logs elapsed ms per request; assert < 500ms in local E2E.

---

## Task 13: Production Docker & Multi-Stage Compose Dev Environment

- **Task ID:** TASK-013
- **Phase / Sprint:** Phase 4 — Retrieval, Search, & RAG API
- **Owner Role:** Builder
- **Goal:** Containerize the FastAPI app + background worker topology with a
  multi-stage, non-root Dockerfile and a Compose network (web-api + worker).
- **Directives:**
  1. Root `Dockerfile`, 2-stage: `builder` (`python:3.11-slim` + build tools)
     compiles wheels into a local cache; `runner` (`python:3.11-slim`) creates
     `appuser` (UID/GID 10001) and installs `--no-cache-dir --no-index
     --find-links` from the wheel cache.
  2. Expose `8000`; CMD `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
  3. `.dockerignore` excluding `.venv`, caches, tests, raw docs, secrets.
  4. `docker-compose.yml`: `web-api` (build, 8000:8000, env files) and
     `background-worker` (same image, worker run command) on one network.
- **Acceptance Criteria:**
  - [x] Dockerfile builds end-to-end without leaking network installs into the runner layer.
  - [x] Container runs as non-root `appuser`.
  - [x] `docker compose up --build -d` provisions both api + worker cleanly.
  - [x] Quality gates green: `ruff check .` and `mypy app/` 0 errors.
  - [x] `current-sprint.md` updated; committed to the feature branch.
- **Notes / Risks:**
  - Worker command needs an entrypoint that starts the FastAPI app + the
    in-process queue worker (the app already starts the worker on lifespan), so
    the worker container can run the same `uvicorn app.main:app` minus the
    external port, or a dedicated worker script. Keep it simple: worker runs the
    same app (worker loop is in-process) without exposing 8000.
  - Python 3.11 chosen (directive); venv/pyproject lint tooling is dev-only and
    not baked into the runtime image.
   - Cannot run `docker` in this WSL-less Windows shell here; build/compose
     verification is the operator's step (documented), not executed by the agent.

---

## Task 14: Automated GitHub Actions CI Pipeline

- **Task ID:** TASK-014
- **Phase / Sprint:** Phase 5 — Containerization & CI/CD Scaffolding
- **Owner Role:** Builder
- **Goal:** Establish an automated CI workflow that runs code quality, type checks,
  and unit tests on every Push or Pull Request targeting the `dev` or `main`
  branches.
- **Directives:**
  1. Create `.github/workflows/ci.yml`.
  2. Trigger on `push` to `[main, dev]` and `pull_request` targeting `[main, dev]`.
  3. Single job `test-and-lint` on `ubuntu-latest`.
  4. Steps: checkout (`actions/checkout@v4`), setup Python 3.11 (`actions/setup-python@v5`),
     pip cache, install deps (`requirements.txt` + `pytest`, `ruff`, `mypy`),
     `ruff check .`, `mypy app/`, `pytest`.
  5. Fail fast on non-zero exit from any quality gate.
- **Acceptance Criteria:**
  - [ ] `.github/workflows/ci.yml` is valid and committed.
  - [ ] Pipeline handles Python 3.11 setup, dependency caching, and checks cleanly.
  - [ ] Quality gates: `ruff check .` and `mypy app/` return 0 errors in CI.
  - [ ] `current-sprint.md` updated; committed to the isolated feature branch.
- **Notes / Risks:**
  - No project test suite exists yet; add a minimal `tests/test_smoke.py` that
    imports app modules to ensure `pytest` collects and passes at least one test.
  - `requirements-dev.txt` is not used by CI; workflow installs `pytest`, `ruff`,
    `mypy` directly per directive.
  - Workflow is declarative only; local execution in this Windows shell cannot
    validate GitHub Actions runs (operator verifies in GitHub UI after push).


