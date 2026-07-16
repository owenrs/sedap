# Knowledge — Environment

Reference for local environment configuration and credentials handling.

## Local Services
[To be defined]

## Environment Variables (`.env.local`, git-ignored)
| Variable | Purpose | Exposure |
|----------|---------|----------|
|          |         |          |


## Rules
- Never hardcode secrets in code; keep them in `.env.local`.
- `.env.example` holds **placeholders only** (e.g. `SECRET_CONSTANT=your-secret-value-here`).
- Remove transient tokens from `.env.local` after use.
