# System Vision, Philosophical Pillars, & Architectural Horizon

This document outlines the core technical philosophies, long-term product vision, and engineering roadmap for **SEDAP** (Sequential Extraction, Dense-sparse Retrieval, and Asynchronous Processing). This serves as the North Star for all architectural updates, engineering standards, and future scale.

---

## 👁️ Core Project Vision

**SEDAP** is designed to bridge the gap between simple, prototype-grade semantic search loops and resilient, multi-tenant enterprise RAG systems. The objective is to provide a zero-leak, deterministic, and highly observable context retrieval engine that serves precision memory directly into conversational orchestration boundaries.

We treat knowledge as a streaming utility: ingestion should be entirely non-blocking to the application threads, and retrieval must balance literal keyword context with latent vector-space semantics.

---

## 🏛️ Strategic Engineering Pillars

### 1. Data-Driven Asynchrony (Separation of Concerns)
A web application should never stall its execution threads to calculate intensive file extraction or vector chunk modifications. SEDAP strictly isolates incoming API ingress requests from heavy cryptographic and multi-dimensional matrix operations using an abstract, async background processor.

### 2. Polymorphism Over Strict Vendor-Lock
The vector database ecosystem shifts rapidly. SEDAP relies heavily on clean interface abstractions (such as `VectorStorageClient`). Swapping a localized native matrix environment for cloud-scale infrastructure requires exactly zero changes to the underlying service layers.

### 3. Precision Search through Hybrid Fusion
Pure semantic (dense vector) retrieval is inherently prone to missing strict literal keywords, serial numbers, and exact code blocks. Conversely, keyword matching (sparse BM25) fails on abstract thematic concepts. SEDAP mandates parallel execution of both pathways, fused using **Reciprocal Rank Fusion (RRF)** to optimize structural relevance dynamically.

### 4. Zero-Leak Containers & Strict Typing
Infrastructure security and code clarity are not optional features to add post-launch. SEDAP relies on two-stage, rootless container definitions and 100% compliant `mypy` type check boundaries to prevent unexpected runtime execution failures in multi-tenant spaces.

---

## 🗺️ Engineering Horizon & Future Scaling

While Phase 5 successfully secures the local container stack and automated GitHub Actions CI validation, the future roadmap for SEDAP targets distributed horizontal scale:

```
[ Phase 5 Complete ] ──► [ Phase 6: Production Scaling ] ──► [ Phase 7: Advanced Orchestration ]
  - Local Containers        - Distributed Task Queue (Celery/Redis) - Graph-RAG / Parent-Child Chunking
  - Mock Storage Matrix     - External Vector DB (Pinecone/Qdrant)  - Agentic Guardrails & Evaluation
  - Strict CI Validation    - OAuth2 Ingress Security               - Dynamic Token Window Management
```

### 🔴 Phase 6: Production Infrastructure Realization
*   **Decoupled Broker Integration:** Transition the internal, thread-safe memory queue into a distributed message broker environment (e.g., Redis or RabbitMQ) to allow background scaling independent of Web API nodes.
*   **Cloud Production Datastores:** Wire production-grade database instances into the existing abstract vector and sparse collection interfaces to support high-concurrency read/write transactions.
*   **User Multi-Tenancy & Authorization:** Implement strict workspace and organization-level boundary filtering across indices so a singular tenant never leaks semantic context into an unauthorized memory frame.

### 🔴 Phase 7: Intelligence & Optimization Layers
*   **Advanced Ingestion Chunking Strategies:** Implement multi-tier structural parsing, including parent-child grouping paradigms and tabular structural text processing.
*   **Graph-Relational Augmentation:** Augment vector lookups with structural knowledge graphs to execute complex entity relationship extraction across isolated documentation bases.
*   **Automated Evaluation Pipelines:** Build programmatic RAG evaluation suites (e.g., using Ragas metrics) inside the GitHub Actions layer to monitor context retrieval faithfulness and answer relevance automatically before merges.
