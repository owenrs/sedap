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

### 4. Execute
- Implement on a feature branch (never `master`/`dev` directly).
- Keep edits atomic and strictly within scope.

### 5. Verify (mandatory completion gate)
All four reviews must pass before proceeding to Phase 6.

- **Requirement review:** Does the work solve the requested problem? Check against the active acceptance criteria in `tasks/current-sprint.md` / `todo.md`.
- **Technical review:** Is architecture respected? Check against the governing ADR (if any) and `architecture.md` system shape. No unapproved file-tree, schema, or dependency changes.
- **Quality review:**
  - If a test suite is present: `Tests pass`.
  - If no test suite is present: `npm run build` passes + `tsc --noEmit` passes + `npm run lint` passes.
  - Errors are handled gracefully (no unhandled rejections, no raw DB exceptions to the client).
- **Documentation review:**
  - Decisions recorded: architectural/schema/dependency decisions have an ADR in `development/decisions/`; resolution-time choices have a `### Decisions & Rationale` block in `development/issues.md`.
  - Tasks updated: `todo.md` checkboxes reflect actual state.
  - Knowledge promoted: reusable lessons moved to `development/knowledge/` (or `rules.md` if universal); `issues.md` entry has a `**Knowledge:**` pointer.

### 6. Report
- Commit locally with a conventional message.
- Emit the standardized report (see Reporting Format below).
- **Halt.** Do not push; instruct the operator to run `git push`.

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
- Run builds/tests locally before reporting done (`npm run build`, `npm run lint`, `tsc --noEmit`).
- Never run package installers (`npm install`, etc.) unless you are the Architect explicitly authorizing a dependency change via ADR.
- Database/Docker commands must target explicit instances (see `rules.md` → Explicit Environmental Scope).

## Remote Guardrails
- Agents may `git add` / `git commit` **locally only**.
- Autonomous `git push` (and any remote interaction) is **forbidden**.
- After a local commit, halt and let the human operator push.

## Reporting Format (required for completion reports)
- **Status:** brief summary
- **Branch:** current branch
- **Changes:** files modified / functions added
- **Validation:** build/compile output
- **Todo:** todo.md state
- **Commit:** 7-char hash

## Issue & Knowledge Protocol
When work surfaces a bug or decision, follow `agents.md` → **Issue Logging & Knowledge Promotion**: log
it in `development/issues.md` via `development/templates/issue-template.md` (include a `### Decisions &
Rationale` block), and promote the reusable lesson to `development/knowledge/` (or `rules.md` if
universal). Keep `issues.md` as the AI activity ledger + investigation history; permanent knowledge
lives in `knowledge/`.
