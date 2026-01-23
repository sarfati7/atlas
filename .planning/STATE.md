# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2025-01-23)

**Core value:** A new developer can onboard in minutes instead of weeks by seeing everything their team has built
**Current focus:** Phase 2 Complete - Ready for Phase 3

## Current Position

Phase: 2 of 9 (Authentication)
Plan: 3 of 3 in current phase
Status: Phase 2 COMPLETE
Last activity: 2026-01-24 - Completed 02-03-PLAN.md (Password Reset with Email)

Progress: [====......] 21%

## Performance Metrics

**Velocity:**
- Total plans completed: 8
- Average duration: 3.8 min
- Total execution time: 0.50 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 5 | 18 min | 3.6 min |
| 2 | 3 | 12 min | 4.0 min |

**Recent Trend:**
- Last 5 plans: 01-04 (3 min), 01-05 (4 min), 02-01 (4 min), 02-02 (3 min), 02-03 (5 min)
- Trend: stable

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Git stores ONLY content, PostgreSQL stores ALL metadata (critical separation)
- [Roadmap]: RBAC abstractions needed from day one (even if policy is "allow all" for v1)
- [Roadmap]: Profile versioning built into data model from start
- [Roadmap]: CLI needs atomic sync operations (write to temp, then move)
- [Roadmap]: MCP security controls required (consent flows, not auto-execute)
- [01-01]: Used Pydantic BaseModel for domain entities to keep domain layer pure (no SQLModel)
- [01-01]: Single CatalogItem entity with type enum discriminator (SKILL/MCP/TOOL)
- [01-01]: uv as package manager (10-100x faster than Poetry)
- [01-02]: SQLModel tables separate from domain entities (domain purity maintained)
- [01-02]: expire_on_commit=False for async session factory (critical for async context)
- [01-02]: Manual initial migration (autogenerate requires running database)
- [01-04]: asyncio.to_thread for PyGithub (sync library with async interface)
- [01-04]: Conditional content repository (GitHub if configured, else in-memory)
- [01-04]: Permissive authorization for Phase 1 (all checks return True)
- [01-05]: System author UUID (all zeros) for webhook-created items
- [01-05]: HMAC SHA-256 signature verification for webhook security
- [01-05]: Directory prefix mapping for type detection (skills/ -> SKILL, etc.)
- [02-01]: Argon2id password hashing via pwdlib.PasswordHash.recommended()
- [02-01]: Abstract auth service interface in domain layer, JWT implementation in adapters
- [02-01]: Rate limiting (3/min) on registration endpoint via slowapi
- [02-02]: Refresh token in HttpOnly cookie with path=/api/v1/auth (only sent to auth endpoints)
- [02-02]: Generic error message for login failures (prevents email enumeration)
- [02-02]: OAuth2PasswordBearer tokenUrl points to /api/v1/auth/login
- [02-02]: CurrentUser type alias for clean protected route signatures
- [02-03]: Same response for forgot-password whether email exists or not (prevents enumeration)
- [02-03]: 30-minute token expiry via itsdangerous max_age_seconds
- [02-03]: Console email service for dev (prints to stdout), SMTP for production

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Phase 1 Completion Summary

All 5 success criteria from ROADMAP.md are met:

1. PostgreSQL database models exist (01-02)
2. Git repository integration exists (01-04)
3. Webhooks/sync mechanism keeps database in sync (01-05)
4. Authorization abstraction exists (01-04)
5. Schema versioning with Alembic (01-02)

## Phase 2 Completion Summary

All 4 success criteria from ROADMAP.md are met:

1. User can create account with email and password (02-01)
2. User can log in and stay logged in across sessions (02-02)
3. User can log out from any page (02-02)
4. User can reset password via email (02-03)

## Session Continuity

Last session: 2026-01-24
Stopped at: Phase 2 complete - all authentication flows working
Resume file: None
Next: Phase 3 - Catalog Backend
