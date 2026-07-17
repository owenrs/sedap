# SEDAP — Workflow

The standardized lifecycle, branching policy, commit format, and local execution protocols every agent follows. Read `rules.md` (conventions) and `onboarding.md` (doc map) first.

## The 6-Phase Task Lifecycle

### 1. Read
- Re-read `rules.md`, `issues.md`, and `todo.md` before any work.
- Confirm the active branch and that you are on the designated next task.

### 2. Select
- Identify the single next task from `tasks/current-sprint.md` / `todo.md`.
- Verify dependencies are satisfied and no open issue blocks the target files.

### 3. Plan
- Output a 2-sentence plan for that one task.
- Ask the human for permission before writing code (unless explicitly pre-approved).
- **Branch Prerequisite:** Once the plan is approved, the very first command executed MUST be creating the task branch. Do not modify workspace files on `dev` or `master`.

### 4. Execute
- **Branch Verification:** Confirm you have successfully checked out the dedicated feature branch. Name it exactly following the pattern: `feature/TASK-XXX-short-slug` (matching the Task ID from `current-sprint.md`).
- Implement the task, keeping edits atomic and strictly within scope.

### 5. Verify (mandatory completion gate)
All four reviews must pass before proceeding to Phase 6.

- **Requirement review:** Does the work solve the requested problem? Check against the active acceptance criteria in `tasks/current-sprint.md` / `todo.md`.
- **Technical review:** Is architecture respected? Check against the governing ADR (if any) and `architecture.md` system shape. No unapproved file-tree, schema, or dependency changes.
- **Quality review:**
  - If a test suite is present: `Tests pass` (e.g., `pytest` for Python backend, `vitest`/`playwright` for frontend).
  - **If no test suite is present:**
    - **Frontend:** `npm run build` passes + type checks pass (`tsc --noEmit` if TypeScript) + `npm run lint` passes.
    - **Backend (Python):** Python syntax/types compile without error, and standard linter/format checks pass (`ruff check .`, `black --check`, or `flake8` as defined in `rules.md`).
  - Errors are handled gracefully (no unhandled rejections, no raw DB exceptions to the client).
- **Documentation review:**
  - Decisions recorded: architectural/schema/dependency decisions have an ADR in `development/decisions/`; resolution-time choices have a `### Decisions & Rationale` block in `development/issues.md`.
  - **Tasks updated:** The agent MUST explicitly check off the completed task checkboxes `[x]` inside `development/tasks/current-sprint.md` before proceeding to Phase 6. High-level roadmap items in `todo.md` remain unchecked until the operator integrates the feature branch.
  - Knowledge promoted: reusable lessons moved to `development/knowledge/` (or `rules.md` if universal); `issues.md` entry has a `**Knowledge:**` pointer.

### 6. Report
- Commit locally with a conventional message.
- Synchronize work: Execute `git push origin feature/TASK-xxx` to publish the completed feature branch to the public GitHub repository.
- Emit the standardized report.

## Branch & Merge Policy (Dev-First)
- **`master`:** production/stable only. Never commit or merge directly into it.
- **`dev`:** the integration branch. Branch features off `dev`; merge back into `dev` when complete.
- **Feature branches:** name as `feature/<issue>-<slug>` (e.g., `feature/issue-3-4-operating-system`).
- **Promotion:** `dev` → `master` only via explicit operator approval after integration testing.

## Commit Format (Conventional Commits)
- Subject line: `<type>: <concise summary>` (max ~72 chars). Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `style`.
- Use an **expanded commit body** for context when the *why* is non-obvious: explain the motivation, the governing ADR (if any), and any trade-offs. Separate body from subject with a blank line.
- Reference the issue/ADR when applicable (e.g., `See ADR-002`, `Closes #3`).

Example:
```
docs: establish strict operating contracts for agent roles in agents.md

Converts passive job descriptions into non-negotiable operating contracts
with explicit Authority, Inputs, Outputs, Boundaries, and Forbidden Actions.
Governs Architect/Builder/QA personas; see ADR-001 for auth context.
```

## Local Execution Protocols
- Run builds/tests locally before reporting done using the appropriate stack commands (e.g., `pytest` / `ruff` for backend, `npm run build` / `tsc` for frontend).
- Never run package installers (`npm install`, `pip install`, `poetry add`, etc.) unless you are the Architect explicitly authorizing a dependency change via ADR.
- Database/Docker commands must target explicit instances (see `rules.md` → Explicit Environmental Scope).

## Remote Guardrails
- **Allowed:** Agents are authorized to run `git push` ONLY to synchronize their active, assigned `feature/` branches with the remote repository.
- **Forbidden:** Agents must NEVER push directly to `dev` or `master` (`main`), nor attempt to merge branches or open Pull Requests autonomously. The human operator retains sole authority over branch integration on the main development streams.

## Reporting Format (required for completion reports)
- **Status:** brief summary
- **Branch:** current branch
- **Changes:** files modified / functions added
- **Validation:** build/compile/linter output
- **Todo:** todo.md state
- **Commit:** 7-char hash

## Issue & Knowledge Protocol
When work surfaces a bug or decision, follow `agents.md` → **Issue Logging & Knowledge Promotion**: log
it in `development/issues.md` via `development/templates/issue-template.md` (include a `### Decisions &
Rationale` block), and promote the reusable lesson to `development/knowledge/` (or `rules.md` if
universal). Keep `issues.md` as the AI activity ledger + investigation history; permanent knowledge
lives in `knowledge/`.
