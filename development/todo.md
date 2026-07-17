# SEDAP — Master Roadmap

## Phase 1: Environment & Architecture Scaffolding
- [x] Milestone: Core stack baseline & WSL local routing verified
- [x] Milestone: Configuration layer & Multi-environment baseline (.env)
- [x] Milestone: Establish Code Quality Gates (Ruff & Mypy)

## Phase 2: Ingestion & Processing Layer
- [x] Milestone: Async document processing pipeline (extractor -> chunker)
  - *Directives:* Implement background workers (e.g., Celery or Arq) to process PDFs, TXT, and Markdown files asynchronously.
  - *Validation:* Fast, non-blocking ingestion endpoint returning 202 Accepted; strict validation on file boundaries and encoding.
- [x] Milestone: Chunking & Text Splitting Engine
  - *Directives:* Implement semantic or token-based splitters with overlapping margins to keep contextual integrity.
  - *Validation:* Unit tests verifying chunk limits, overlaps, and Metadata preservation (source file, UUID, page numbers).
- [x] Milestone: Entity Extraction Service integration
  - *Directives:* Hook up an NLP parser (or lightweight local spaCy/instructor-LLM layer) to extract key metadata entities from chunks.

## Phase 3: Vector Storage & Embedding Layer
- [x] Milestone: Embedded vector database baseline (Qdrant / pgvector)
  - *Directives:* Spin up the database instance (local docker-compose) and write the asynchronous client connection factory.
- [x] Milestone: Embedding Generation & Synchronization Engine (Local + Cloud API toggle)
  - *Directives:* Integrate Sentence-Transformers or OpenAI embedding API; build bulk upsert pipelines with strict error/retry handling.
  - *Validation:* Querying database returns semantically similar records with a cosine similarity score.
- [x] Milestone: Semantic search endpoint & query router

## Phase 4: Retrieval, Search, & RAG API
- [x] Milestone: Chat Completion & Context Assembly Service
  - *Status:* Completed in TASK-010! Scaffolded `LLMService` ABC, `MockLLMProvider`, `OpenAILLMProvider`, `RAGOrchestrator`, and POST `/api/v1/query`.
- [ ] Milestone: Hybrid Search implementation (Keyword BM25 + Dense Vector)
  - *Directives:* Combine exact text matching with semantic vector search; implement Reciprocal Rank Fusion (RRF) for ranking. (Up next in TASK-011!)
- [ ] Milestone: End-to-end Chat and Search REST endpoints
  - *Directives:* Secure and optimize the combined endpoints, verify fast API response times under 500ms, and ensure strict Pydantic payload models.

## Phase 5: Containerization & CI/CD Scaffolding
- [ ] Milestone: Docker & Local Compose Dev Environment
  - *Directives:* Containerize the FastAPI application; compile light Alpine or slim-Debian multi-stage builds.
- [ ] Milestone: Automated GitHub Actions CI Pipeline
  - *Directives:* Run Ruff, Mypy, and Pytest automatically on every Pull Request to `dev` or `main`.