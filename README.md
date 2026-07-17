# Modern Hybrid RAG Engine: Operator's Manual & User's Guide

Welcome to your production-grade Retrieval-Augmented Generation (RAG) engine. This system is engineered as a decoupled, asynchronous, type-safe Python application designed to ingest unstructured text, process it via parallel retrieval tracks, and serve contextually accurate information over multi-turn conversations.

This guide provides everything you need to operate, test, and interact with your new architecture.

---

## 🏗️ System Architecture at a Glance

Before booting up the system, it helps to understand how data flows through the engine:

```
[ Client Request ] ──► [ FastAPI Web API ] ──► [ In-Memory Task Queue ]
                              │                         │
      ┌───────────────────────┘                         ▼
      ▼                                       [ Async Background Worker ]
[ Hybrid Search ]                                       │ (Token-bounded Chunking)
  ├── Dense (Embeddings Matrix)                         ▼
  └── Sparse (BM25 Keyword Engine)              [ Vector/Sparse Storage ]
      │
      ▼
[ Reciprocal Rank Fusion (RRF) ] ──► [ Context Synthesis ] ──► [ Client Response ]
```

---

## 🚀 Quick Start: How to Run the System

You have two isolation patterns ready for runtime deployment.

### Path A: The Production Footprint (Docker Compose)
This boots the entire decoupled stack—the Web API frontend and the asynchronous background processing worker—in isolated, low-privilege containers.

**1. Boot the Stack:**
Execute this command in your root directory to build and view live streaming logs:
```bash
docker compose up --build
```
*Look for the confirmation line: `INFO: Uvicorn running on http://0.0.0.0:8000`*

**2. Tear Down the Stack:**
To gracefully stop and destroy the containers without leaking resources, press `Ctrl + C` and execute:
```bash
docker compose down
```

### Path B: The Sandbox Footprint (Local Virtual Environment)
Perfect for rapid local iteration, debugging, or code modification.

**1. Activate the Virtual Environment:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**2. Boot the API Server with Live-Reloading:**
```bash
uvicorn app.main:app --reload
```
*The `--reload` flag automatically restarts the application the moment you save changes to any `.py` file.*

---

## 🕹️ Interacting with the API via Swagger UI

Once your server is running via either path, open your browser and navigate to:
👉 **`http://localhost:8000/docs`**

This loads the interactive **FastAPI Swagger UI**, allowing you to execute live operations against your engine without writing client-side code.

### 1. Document Ingestion Pipeline
To ingest knowledge into your system:
* Locate the **`POST /api/v1/ingest`** endpoint.
* Click **"Try it out"**.
* Modify the request body to pass your text payload:
  ```json
  {
    "source_name": "architecture_overview.txt",
    "content": "The system utilizes an in-memory task queue paired with a custom token-bounded recursive chunker to isolate intensive I/O blocking jobs from the primary web application threads."
  }
  ```
* Click **Execute**.

> **What happens behind the scenes:** The API instantly returns a `202 Accepted` status along with a tracking ID. It throws the workload into the async queue, freeing your API thread immediately. In the background worker terminal, you will see the logs trace the token-bounded recursive chunker splitting and writing the data to storage.

### 2. Executing Hybrid Fusion Search
To query your ingested knowledge base:
* Locate the **`POST /api/v1/search`** endpoint.
* Click **"Try it out"**.
* Modify the payload to submit your query:
  ```json
  {
    "query": "How are blocking jobs handled?",
    "top_k": 3
  }
  ```
* Click **Execute**.

> **What happens behind the scenes:** The engine simultaneously calculates the Dense Retrieval (Vector embedding matrix cosine similarity) and Sparse Retrieval (BM25 keyword matching frequency). It routes both result lists into a Reciprocal Rank Fusion ($k=60$) mathematical layer, resolving ranking anomalies to return the most contextually relevant chunks.

---

## 🧪 Operational Maintenance & Health Verification

To guarantee code quality and pipeline resilience remain green before code changes or deployment steps, run your automated validation suites locally.

### 1. Run the Test Suite
Ensure all internal mechanics, ingestion loops, and mock retrieval spaces function flawlessly:
```bash
.\.venv\Scripts\pytest -v
```

### 2. Verify Code Formatting & Quality
Enforce strict formatting, checking for unused imports, dead variables, or formatting anomalies:
```bash
.\.venv\Scripts\ruff check .
```

### 3. Verify Strict Type-Safety
Catch silent bugs and type violations across all 22 source files before they reach production:
```bash
.\.venv\Scripts\mypy app/
```

---

## 🛡️ Production CI Gatekeeping
Every time code is pushed or a Pull Request is opened against the `main` or `dev` branches, the automated pipeline in `.github/workflows/ci.yml` spins up an isolated Linux architecture runner, configures a cached Python environment, installs dependencies, and runs all three verification suites. 

**Keep your local environments clean, and your GitHub build badge will stay permanently green!**
