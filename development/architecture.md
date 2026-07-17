# SEDAP — Architecture

## System Shape

FastAPI async backend + SvelteKit/React frontend, connected via REST API. The backend follows a layered architecture: routes → services → repositories → models. Background processing (extraction, chunking, embedding, entity extraction) runs via FastAPI `BackgroundTasks` or a task queue. The frontend is a thin client that orchestrates uploads, search, and chat through typed API calls.

```
frontend (SvelteKit / React)
    │  REST/JSON + SSE
    ▼
FastAPI app (app/main.py)
    │
    ├── API routes (app/api/v1/)
    │       ├── documents.py   — upload, status, entities
    │       ├── search.py      — semantic search
    │       └── chat.py        — RAG chat, sessions
    │
    ├── Services (app/services/)
    │       ├── extractor.py   — PDF/TXT/MD parsing
    │       ├── chunker.py     — recursive text splitting
    │       ├── embedder.py    — vector generation
    │       ├── searcher.py    — pgvector cosine similarity
    │       ├── rag.py         — retrieval + generation
    │       └── entity.py      — entity/concept extraction
    │
    ├── Repositories (app/repositories/)
    │       ├── documents.py   — document CRUD
    │       ├── chunks.py      — chunk + vector queries
    │       ├── entities.py    — entity persistence
    │       └── chat.py        — sessions + messages
    │
    ├── Models (app/models/)   — SQLAlchemy 2.0 async models
    ├── Schemas (app/schemas/)  — Pydantic v2 request/response
    └── Tasks (app/tasks/)      — background indexing jobs
```

## Component Responsibilities

### Backend (FastAPI)

**Routes (`app/api/v1/`)**
- Define request/response contracts via Pydantic schemas.
- Enforce auth, rate limits, and CORS at the router level.
- Delegate immediately to services; contain no business logic.

**Services (`app/services/`)**
- Single-responsibility modules: one service per domain action.
- `extractor.py`: parse raw bytes into clean text (PDF via `pypdf` or `pdfplumber`; plain text passthrough).
- `chunker.py`: recursive character splitting with overlap; configurable chunk size.
- `embedder.py`: call embedding model (OpenAI or local); return float vectors.
- `searcher.py`: accept a query vector, run `cosine_similarity` against `chunks.embedding`, return top-k.
- `rag.py`: bundle retrieved chunks into a prompt, call LLM, return grounded answer with citations.
- `entity.py`: extract entities from document text via LLM or regex; persist to `entities` table.

**Repositories (`app/repositories/`)**
- Isolate all SQLAlchemy async session usage.
- Expose methods like `create_document`, `get_chunks_by_document`, `similarity_search`, `create_chat_message`.
- Never leak ORM models to routes or services.

**Background Tasks**
- File upload triggers an async indexing pipeline: extract → chunk → embed → store vectors → extract entities.
- Long-running LLM calls and embedding generation must not block the request handler; use `BackgroundTasks` or a task queue.

### Frontend (SvelteKit / React)

**Pages/Routes**
- `/upload` — drag-and-drop file upload with progress; polls document status.
- `/documents/[id]` — document viewer with chunk highlighting.
- `/search` — semantic search input; renders matching passages with similarity scores.
- `/chat` — RAG chat interface with clickable citation numbers mapped to source chunks.
- `/entities` — sidebar/list of extracted entities with document context.

**Components**
- `FileUploader.svelte` / `FileUploader.tsx` — multipart upload via `FormData`; displays upload progress and parsing status.
- `SearchResults.svelte` — renders ranked chunks with highlighted source locations.
- `ChatInterface.svelte` — streaming message bubbles; citations link to chunk viewer.
- `EntitySidebar.svelte` — grouped entity cards with context excerpts.

**API Client (`lib/api/`)**
- Single `api.ts` / `api.js` module wrapping `fetch` with base URL, auth headers, and error normalization.
- All endpoints return typed DTOs matching backend Pydantic schemas.

## Database (see `decisions/`)

### Core Tables

| Table | Purpose |
|-------|---------|
| `documents` | Uploaded file metadata: filename, content_type, size, status, storage_path, timestamps |
| `chunks` | Text chunks with `embedding` (pgvector), document_id, position, token_count |
| `entities` | Extracted entities: document_id, type (company/date/monetary/person), value, context_snippet |
| `chat_sessions` | User chat sessions linked to a document |
| `chat_messages` | Session messages with role, content, and citation references |

### Key Indexes
- `chunks.embedding` → `ivfflat` or `hnsw` index for cosine similarity.
- `chunks.document_id` → btree for per-document queries.
- `entities.document_id` + `entity_type` → btree for sidebar filtering.

## API Contracts

### File Upload
```
POST /api/v1/documents/upload
Content-Type: multipart/form-data
Body: file (binary), metadata (optional JSON)

Response 201:
{
  "id": "uuid",
  "filename": "report.pdf",
  "status": "processing",
  "created_at": "..."
}
```

### Semantic Search
```
POST /api/v1/documents/{document_id}/search
Body: { "query": "string", "top_k": 5 }

Response 200:
{
  "results": [
    {
      "chunk_id": "uuid",
      "content": "...",
      "score": 0.89,
      "page": 3,
      "entities": ["OpenAI", "GPT-4"]
    }
  ]
}
```

### RAG Chat
```
POST /api/v1/chat/sessions
Body: { "document_id": "uuid" }

POST /api/v1/chat/sessions/{session_id}/messages
Body: { "query": "string" }

Response 200 (streaming via SSE):
data: {"type": "token", "content": "The"}
data: {"type": "token", "content": " report"}
data: {"type": "citations", "chunks": [...]}
```

### Entities
```
GET /api/v1/documents/{document_id}/entities
Response 200:
{
  "entities": [
    { "type": "company", "value": "Acme Corp", "context": "..." }
  ]
}
```

## Frontend ↔ Backend Communication

- **Transport:** HTTPS REST with JSON payloads. Chat streaming uses Server-Sent Events (SSE) with `text/event-stream`.
- **Auth:** Bearer token in `Authorization` header; frontend stores token in httpOnly cookie or secure storage.
- **File Uploads:** `FormData` with `multart/form-data`; backend accepts via FastAPI `UploadFile`.
- **Error Handling:** Backend returns RFC 7807 Problem Details or FastAPI `HTTPException` JSON; frontend normalizes into typed error states.
- **CORS:** Restricted to frontend origin(s) via `CORS_ORIGINS` env var; no wildcard in production.

## Key Decisions

Architectural decisions live in `decisions/` as ADRs. This file describes system *shape*; the ADRs explain *why*.

- ADR-001: FastAPI async stack + SQLAlchemy 2.0 over sync frameworks.
- ADR-002: pgvector for vector search instead of dedicated vector DB.
- ADR-003: MinIO for local file storage instead of filesystem or S3-only.
- ADR-004: BackgroundTasks vs Celery for indexing pipeline.
