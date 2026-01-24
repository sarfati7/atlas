# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2025-01-23)

**Core value:** A new developer can onboard in minutes instead of weeks by seeing everything their team has built
**Current focus:** Phase 6 - Web Frontend Core COMPLETE

## Current Position

Phase: 6 of 9 (Web Frontend Core)
Plan: 5 of 5 in current phase
Status: Phase complete
Last activity: 2026-01-24 - Completed 06-04 (catalog detail page)

Progress: [==========] 60%

## Phase 6 Progress

**What:** React web frontend for auth, catalog browsing, and dashboard
**Tech stack:** Vite + React 18 + TypeScript + TanStack Query + shadcn/ui
**Theme:** Dark-only, developer-focused (GitHub-like)

| Plan | Wave | What it builds | Status |
|------|------|----------------|--------|
| 06-01 | 1 | Project setup, API client, dark theme | COMPLETE |
| 06-02 | 2 | Auth pages (login, signup, password reset) | COMPLETE |
| 06-03 | 2 | Catalog browser with cards and filters | COMPLETE |
| 06-04 | 3 | Catalog detail page with documentation | COMPLETE |
| 06-05 | 2 | User dashboard | COMPLETE |

**Key docs:**
- `.planning/phases/06-web-frontend-core/06-CONTEXT.md` - User decisions
- `.planning/phases/06-web-frontend-core/06-RESEARCH.md` - Tech research
- `.planning/phases/06-web-frontend-core/06-01-SUMMARY.md` - Completed plan summary

## Performance Metrics

**Velocity:**
- Total plans completed: 20
- Average duration: 3.5 min
- Total execution time: 1.25 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 5 | 18 min | 3.6 min |
| 2 | 3 | 12 min | 4.0 min |
| 3 | 2 | 8 min | 4.0 min |
| 4 | 3 | 8 min | 2.7 min |
| 5 | 2 | 6 min | 3.0 min |
| 6 | 5 | 26 min | 5.2 min |

**Recent Trend:**
- Last 5 plans: 06-02 (4 min), 06-03 (5 min), 06-05 (5 min), 06-04 (2 min)
- Trend: Phase 6 complete, all frontend plans executed efficiently

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
- [03-01]: PaginatedResult as dataclass in domain layer (not Pydantic) for domain purity
- [03-01]: Page-based pagination (1-indexed) vs cursor-based for simplicity
- [03-01]: Max page size 100 enforced at API level via Query validation
- [03-01]: Search uses ILIKE on name, description, tags (case-insensitive)
- [03-02]: Documentation is optional - missing README returns empty string, not error
- [03-02]: README path derived from git_path directory (skills/foo/config.yaml -> skills/foo/README.md)
- [04-01]: UserConfiguration uses Pydantic BaseModel (same as User/CatalogItem) for domain purity
- [04-01]: ConfigurationVersion is dataclass (not Pydantic) for simple value object
- [04-01]: user_id unique constraint enforces one config per user
- [04-01]: git_path also unique to prevent collision if paths change
- [04-02]: Upsert logic handles both config.id lookup and user_id collision
- [04-02]: In-memory version history returns single 'current' version for testing simplicity
- [04-03]: ConfigurationService orchestrates git content + database metadata operations
- [04-03]: All configuration endpoints require authentication via CurrentUser
- [04-03]: File import validates .md extension, UTF-8 encoding, 1MB size limit
- [04-03]: Rollback creates new commit with old content (preserves full history)
- [04-03]: GET /me returns empty content if user has no config yet (no error)
- [05-01]: EffectiveConfiguration as dataclass (not Pydantic) for simple value object
- [05-01]: Configuration sections merged with --- separator and # headers for org/team/user
- [05-01]: get_available_items returns empty list if user doesn't exist (graceful degradation)
- [05-01]: asyncio.gather for parallel repository fetches in service methods
- [05-02]: EffectiveConfigurationResponse shows boolean flags for org/team/user applied
- [05-02]: Available-items filter uses Query param with Optional[CatalogItemType]
- [05-02]: UserNotFoundError returns 404 on dashboard (vs empty list for available-items)
- [06-01]: Dark-only theme using OKLCH color space (GitHub aesthetic)
- [06-01]: createBrowserRouter pattern (not BrowserRouter with Routes)
- [06-01]: Request queue pattern for concurrent 401 handling
- [06-01]: auth:logout custom event for store cleanup on refresh failure
- [06-02]: OAuth2 form data format for login (username field contains email)
- [06-02]: Forgot password toggles form in place rather than separate route
- [06-02]: Registration shows success screen, requires manual login afterward
- [06-02]: Reset password validates token from URL query param
- [06-03]: Feature directory structure (features/catalog/ with api/, hooks/, components/)
- [06-03]: CatalogQueryParams renamed from CatalogFilters to avoid component name conflict
- [06-03]: Type-colored badges (blue SKILL, purple MCP, green TOOL)
- [06-03]: RootLayout wraps all app routes (catalog, dashboard, settings)
- [06-05]: protectedLoader checks Zustand store directly (no async API call)
- [06-05]: guestLoader redirects authenticated users from login/signup to dashboard
- [06-05]: Profile feature uses standard module pattern (api/hooks/components)
- [06-04]: Type badge colors: emerald SKILL, blue MCP, amber TOOL for detail page
- [06-04]: DocumentationViewer with react-markdown and remark-gfm for README rendering

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

## Phase 3 Completion Summary

All 6 success criteria from ROADMAP.md are met:

1. API returns all skills available company-wide with metadata (03-01)
2. API returns all MCPs available company-wide with metadata (03-01)
3. API returns all tools available company-wide with metadata (03-01)
4. API supports keyword search across catalog items (03-01)
5. API supports filtering by type (skill/MCP/tool) (03-01)
6. Each catalog item includes documentation (03-02)

Catalog API endpoints:
- GET /api/v1/catalog - paginated list with type filter and search
- GET /api/v1/catalog/{item_id} - detail with README documentation

## Phase 4 Completion Summary

All 5 success criteria from ROADMAP.md are met:

1. API accepts and persists claude.md configuration edits (04-03)
2. All configuration changes are committed to git-backed repository (04-03)
3. API returns version history for user's configuration (04-03)
4. API supports rollback to any previous configuration version (04-03)
5. API accepts import of existing claude.md content (04-03)

Configuration API endpoints:
- GET /api/v1/configuration/me - get current config
- PUT /api/v1/configuration/me - update config
- GET /api/v1/configuration/me/history - version history
- POST /api/v1/configuration/me/rollback/{sha} - rollback
- POST /api/v1/configuration/me/import - file upload

## Phase 5 Completion Summary

All success criteria from ROADMAP.md are met:

1. API returns user dashboard with teams, item counts, config status (05-02)
2. API returns available catalog items for user (05-02)
3. API returns effective configuration with inheritance (05-02)

Profile API endpoints:
- GET /api/v1/profile/dashboard - user dashboard data
- GET /api/v1/profile/available-items - catalog items with optional type filter
- GET /api/v1/profile/effective-configuration - merged config with source breakdown

## Phase 6 Completion Summary

All success criteria from ROADMAP.md are met:

1. User can log in/log out (06-01, 06-02)
2. User can browse catalog with search and type filtering (06-03)
3. User can view catalog item details with documentation (06-04)
4. User can view their dashboard (06-05)
5. Protected routes redirect unauthenticated users (06-05)

Frontend pages:
- /login - Login with email/password
- /signup - User registration
- /reset-password - Password reset flow
- /catalog - Browse catalog with search and filters
- /catalog/:id - View item detail with README documentation
- /dashboard - User dashboard with profile info

## Session Continuity

Last session: 2026-01-24
Stopped at: Completed 06-04-PLAN.md (Catalog detail page)
Resume file: None
Next: Phase 7 or deployment testing
