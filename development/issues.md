# Repository Issue & Resolution Ledger

AI activity ledger: agents log issues they encounter during work here (humans may also add). Each
resolved entry records a **Decisions & Rationale** block (what was decided + why) and promotes the
reusable lesson to `knowledge/`. Architectural decisions additionally live as ADRs in `decisions/`.
Permanent solutions belong in `knowledge/` (or `rules.md` when universal) — this file is the
active-bug + investigation-history record. See `agents.md` → Issue Logging & Knowledge Promotion.

## [ISSUE-009] WSL Ubuntu Python 3.14.4 ships without pip/ensurepip; apt install times out
- **Status:** Resolved (operator bootstrapped pip in WSL) — TASK-001 resumed
- **Date Logged:** 2026-07-17
- **Symptom:** In WSL `Ubuntu` distro, `python3 --version` → `Python 3.14.4` (OK), but `pip` is not on PATH, `python3 -m pip` → `No module named pip`, and `python3 -m ensurepip` → `No module named ensurepip`. `sudo apt-get install -y python3-pip` did not complete within 120s (no output; suspected no network egress or stalled mirror inside WSL).
- **Root Cause:** Base Ubuntu image has a minimal Python install without the `pip`/venv ensurepip bootstrap, and the package manager cannot reach its mirror from this WSL instance.
- **Target File(s):** environment toolchain (no project file yet); `development/knowledge/environment.md` (needs a WSL pip-bootstrap note once resolved).
- **Resolution Strategy:** Choose one and confirm with operator: (a) `sudo apt-get install python3-pip python3-venv` on a working network; (b) `sudo apt-get install python3-full` (brings ensurepip); or (c) bootstrap pip via `get-pip.py` once network is available. Until pip exists, the `.venv` creation (`python3 -m venv`) and `fastapi` install cannot proceed.
- **Resolution Status:** [x] Resolved — operator installed pip in WSL Ubuntu
- **Knowledge:** see `development/knowledge/environment.md` → "WSL pip bootstrap (Ubuntu distro)"

### Decisions & Rationale
- **Decision:** Halt execution of TASK-001 at environment verification; log the anomaly rather than fabricate a `.venv`/FastAPI install.
- **Why:** The workflow's Verify gate and the agents.md self-verification gate forbid reporting "done" while an observed incident is unlogged; pip is a hard prerequisite for criteria 1–3.

### Resolution Note (2026-07-17 10:05 +08:00)
- Operator bootstrapped pip inside WSL Ubuntu. Verified: `python3 -m pip --version` → `pip 25.1.1`, `python3 -m ensurepip --version` → `pip 25.1.1`. Criterion 1 now satisfied; TASK-001 continued (venv + fastapi + placeholder main.py + boot check).