# Issue Template

Copy this block when logging a bug/incident in the issue ledger (`development/issues.md`). This file is
the AI activity ledger + investigation history; promote reusable lessons to `development/knowledge/`.

## [ISSUE-XXX] Short Title
- **Status:** Open
- **Date Logged:** YYYY-MM-DD
- **Symptom:** What the user/operator observes (exact error text when possible).
- **Root Cause:** Why it happens (file/function/mechanism).
- **Target File(s):** `path/to/file.ts`
- **Resolution Strategy:** How it will be fixed.
- **Resolution Status:** [ ] Pending Agent Execution
- **Knowledge:** see `development/knowledge/...` (add after resolution promotes the lesson)

### Decisions & Rationale
- **Decision:** What was decided during resolution.
- **Why:** One-line reason for the decision (architectural/schema/dependency decisions also get a formal ADR in `development/decisions/`).

### Resolution Note (YYYY-MM-DD HH:MM +08:00)
- What was changed and why.
- Verification evidence (build output, query result).
