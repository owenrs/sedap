# SEDAP — Coding Conventions & Non-Negotiable Constraints

Immutable coding laws, security rules, and architectural principles. Onboarding, workflow, agent contracts, and architecture live in their own files (see `onboarding.md` → Document Map).

## 1. TypeScript & Framework Conventions
- **TypeScript strict:** every file strictly typed; avoid `any`. Prefer `interface` over `type` for public contracts.
- **Folder structure:** components in `/components` (flat or logical groups); 
- **Documentation:** JSDoc on every interface, public helper, and custom hook explaining *why*; never comment the obvious.

## 2. Styling Conventions
- **No custom CSS or inline styles** No custom CSS or inline styles unless strictly necessary.

## 3. Code Discipline Constraints
- **No Side-Effects:** do not modify files outside the current task's scope.
- **Verify, Don't Guess:** if a dependency or schema is unclear, pause and ask.
- **Keep Code Atomic:** one responsibility per file; split files beyond ~250 lines.
- **Token Conservation:** edit only changed blocks; explain *why* only when asked or when logic is complex.
- **Anti-Looping:** if a command/build fails twice with the same/similar error, STOP and escalate to the human with the error and the two distinct attempts. Never attempt a third automated fix.

## 4. Security & Environment Isolation
- **No hardcoded secrets** (keys, passwords, connection strings, JWTs) in code.
- Secrets/environment config live in `.env.local` (git-ignored); `.env.example` holds **placeholders only**.

## 5. Scalable Architectural Principles
Reactive symptoms, translated into forward-looking constraints so they never recur:

- **Single Source of Truth:** Infrastructure dependencies and API client initializations must have a single provider/singleton. All consumer files must import from this provider (e.g., `@/lib/supabase`). Never instantiate duplicate clients.
- **Strict Environment Isolation:** Secrets and configuration variables must reside in `.env.local` and be read strictly via environment abstractions. Never expose raw string keys in version-controlled code.
- **Explicit Environmental Scope:** Commands that execute database modifications or Docker operations must explicitly target specific connection strings or flags. Never rely on default system schemas or implicitly targeted database instances.
