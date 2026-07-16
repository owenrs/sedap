# Knowledge — Troubleshooting

Actionable workarounds for environment-specific failures, grouped by category. The QA / Copilot appends newly discovered gotchas and successful prompt patterns here after each task (see `agents.md` → Post-Task Handoff Protocol). Keep entries concise, actionable, and this file lightweight.

## Docker
- **Bypassing Supabase CLI Migration Failures (Windows):** If the native Windows CLI fails with a `FileSystem.readFile` or `PgClient connection` error when running migrations (e.g. `supabase migration up` → `NotFound: FileSystem.readFile (C:\Users\<user>\.supabase\profile)`), bypass the CLI and apply the migration directly to the local Docker container.

  > The local container is **raw PostgreSQL** (`postgres:15-alpine`, `POSTGRES_DB=ampcs`), not a Supabase stack — so connect to the `ampcs` database, **not** `postgres`.

  ```powershell
  # From the project root; stream the SQL file into the container
  Get-Content .\supabase\migrations\<migration_file_name>.sql | docker exec -i ampcs_db psql -U postgres -d ampcs -f -
  ```

  - **Caveats:** This raw Postgres container has **no `auth` schema / RLS** — it cannot stand in for the hosted Supabase project's full schema. The `supabase db push` attempt against the *hosted* project failed separately with `permission denied for schema auth` (SQLSTATE 42501) because the local migration creates a mock `auth` schema. That is a hosted-project migration concern, unrelated to the Windows CLI bug.

  - **Schema cache gap after writing a migration:** Adding a `.sql` file under `supabase/migrations/` does **not** alter the running database. Until the migration is applied, the app throws `Could not find the '<col>' column of '<table>' in the schema cache` at runtime. After writing a migration, apply it locally via the bypass above (`-d ampcs`), then verify with `\d <table>` inside the container. This pattern was used and confirmed for the `chaos_settings` jsonb column (TASK-005 / ADR-004): `ALTER TABLE` + `COMMENT` succeeded, column appeared in `\d mock_endpoints`, and the schema-cache error cleared. Verified migration ≠ applied migration.

## Git
- **Worktree branch collision blocks `git checkout`:** If `git checkout <branch>` fails with
  `fatal: '<branch>' is already checked out at '<path>'`, a git worktree (often under `.kilo/worktrees/`
  from a parallel agent instance) holds that branch. You cannot check it out in the main repo until the
  worktree is removed.
  - Inspect first: `git worktree list`.
  - Confirm safe to remove: ensure the worktree status is clean (`git -C <path> status --short` shows no
    modified tracked files) and the branch is already in `dev` (`git merge-base --is-ancestor <branch> dev`
    returns true, and `git rev-list dev..<branch>` is empty) so no committed work is lost.
  - Back up untracked files (they are deleted by `worktree remove`): copy any `??` files out first.
  - Remove: `git worktree remove <path> --force` (force needed if the worktree's git process crashed),
    then `git worktree prune`, then `git branch -d <branch>`.
  - (See `issues.md` → ISSUE-008.)

## Agent Discipline
- **Log every observed anomaly, then verify before saying "done":** A documented logging protocol only works if it fires. If you observe or resolve any anomaly — inside or outside an active task (env/tooling crashes, parallel-instance issues, user-reported failures) — log it in `issues.md` with a `### Decisions & Rationale` block and promote the lesson to `knowledge/`. Before reporting completion, self-check that the incident was actually logged; never declare "done" while an observed incident is unlogged. (See `issues.md` → ISSUE-009; convention in `agents.md` → Issue Logging & Knowledge Promotion, step 5.)

## Local Hangs
- (Add dev-server, build, or install hang workarounds here.)


