# SEDAP — Onboarding

The single entry point for any agent or contributor joining the project. Read this first, then follow the Document Map to the file you need.

## 📋 Project Overview: The Semantic Document Analyzer

The objective of this app is to let users upload dense, unstructured documents (PDFs, TXT files, Markdown, or financial reports) and interact with them using natural language.

Instead of basic keyword matching (ctrl+F), this app utilizes semantic vector embeddings. It understands the meaning behind a user's query and surfaces the exact passages of a document that answer their question, alongside an AI-synthesized summary.

## ⚡ Core Capabilities
**1. Robust Document Ingestion & Chunking Pipeline**
- Parsing: Extracting clean raw text from PDF/TXT uploads, filtering out messy formatting or page numbers.
- Recursive Chunking: Splitting the text into readable "chunks" (e.g., 500 characters each) with a 100-character overlap, so context isn't lost at the boundaries.
- Embedding Generation: Sending those chunks to an embedding model (like OpenAI's text-embedding-3-small or a local HuggingFace model) to convert text into mathematical coordinate vectors.

**2. Semantic Search Engine (No-LLM Mode)**
Before invoking a text generator to "answer" questions, the system must perform raw mathematical semantic retrieval.

- The user types a query.
- The system converts the query into a vector.
- The backend performs a cosine similarity search against the database to find the top 3–5 most relevant document chunks.
- UI Capability: The frontend displays these exact matching passages to the user, highlighting where they were found in the source document.

**3. RAG (Retrieval-Augmented Generation) Chat**
Once retrieval works, you plug in the "generation" layer.

- The system retrieves the top chunks, bundles them into a system prompt (e.g., "Answer the query using only the following context..."), and passes it to a chat model (like Claude or GPT).
- The user gets a clean, conversational answer.
- Footnote Citations: The UI must include clickable citation numbers mapping directly to the source chunks retrieved in Capability 2 (classic GEO/AIO style!).

**4. Automated Entity & Concept Extraction**
The moment a file is uploaded, the backend automatically runs a background task to index it.

- It automatically extracts key entities (companies, dates, monetary values, names) and lists them in a sidebar.
- It generates a 3-bullet summary of the document's main theme so the user knows what it's about before they even ask their first question.

## Philosophy
- **Read first, execute second.** Never modify files before understanding the rules, the active task, and existing decisions.
- **Decoupled by design.** UI, schema, and database logic live in separate, single-responsibility files.
- **Token conservation.** Small, modular files; minimal fluff; precise edits over full rewrites.
- **Immutable Truth.** Canonical project state lives in this documentation system, not in chat history.

## Roles
Three operational personas (see `architecture.md` for the full breakdown):
1. **Architect** — system design, schema, dependency selection.
2. **Builder** — type-safe implementation and Supabase integration.
3. **QA Inspector** — review, type-checking, edge-case prevention.

## Governance
- All work happens on feature branches off `dev`; `master` is production-only (see `rules.md` → Git policy).
- Agents stage and commit locally only; **no autonomous `git push`** (operator runs the push).
- Architectural decisions are recorded as ADRs in `decisions/`.

## Document Map
| Need | Read |
|------|------|
| Coding guardrails & tech limits | `rules.md` |
| Phased execution lifecycle | `workflow.md` |
| Roles, system design, decisions | `architecture.md`, `decisions/` |
| Project direction & goals | `vision.md` |
| Windows/Docker/Env fixes | `knowledge/troubleshooting.md`, `knowledge/environment.md` |
| Current sprint tasks | `tasks/current-sprint.md` |
| New task / issue boilerplate | `templates/` |

### Onboarding Sound-Off Requirement
Upon completing the reading of onboarding materials, the agent MUST issue a formal initialization sign-off matching this exact pattern:
"🚨 SYSTEM ENGAGED // Persona: [Agent Name] // Onboarding Complete. Bounded by [Project Name] OS. Awaiting Task execution."
