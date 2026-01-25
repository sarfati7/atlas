# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2025-01-23)

**Core value:** A new developer can onboard in minutes instead of weeks by seeing everything their team has built
**Current focus:** All phases complete - Milestone 1.0 finished!

## Current Position

Phase: 9 of 9 (Governance & Admin) ✓
Plan: 5 of 5 in current phase
Status: All phases complete
Last activity: 2026-01-26 - Completed 09-05-PLAN.md (usage analytics)

Progress: [==========] 100%

## Phase 8 Handoff

**What:** CLI tool to sync configuration from Atlas to local ~/.claude/CLAUDE.md
**Tech stack:** Python, Typer, httpx, keyring, rich
**Builds on:** Phase 2 auth (JWT tokens), Phase 5 profile API (effective-configuration)

**Success criteria:**
1. CLI installs with single command - DONE (08-01)
2. User can authenticate via browser OAuth flow - DONE (08-02)
3. User can sync configuration to ~/.claude/CLAUDE.md - DONE (08-03)
4. Sync uses atomic writes (no partial files on interrupt) - DONE (08-01, 08-03)
5. CLI shows helpful error messages - DONE (08-04, 08-05)

**Backend endpoints used:**
- POST /api/v1/auth/login - token exchange
- POST /api/v1/auth/refresh - token refresh
- GET /api/v1/profile/effective-configuration - get merged config

**CLI commands delivered:**
- atlas auth login - authenticate with email/password
- atlas auth logout - clear credentials
- atlas auth status - show authentication status
- atlas sync - sync config to local file
- atlas status - show sync status (local vs remote)
- atlas doctor - health check diagnostics

## Performance Metrics

**Velocity:**
- Total plans completed: 33
- Average duration: 3.6 min
- Total execution time: 2.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 5 | 18 min | 3.6 min |
| 2 | 3 | 12 min | 4.0 min |
| 3 | 2 | 8 min | 4.0 min |
| 4 | 3 | 8 min | 2.7 min |
| 5 | 2 | 6 min | 3.0 min |
| 6 | 5 | 26 min | 5.2 min |
| 7 | 5 | 19 min | 3.8 min |
| 8 | 5 | 16 min | 3.2 min |
| 9 | 5 | 20 min | 4.0 min |

**Recent Trend:**
- Last 5 plans: 09-01 (4 min), 09-02 (4 min), 09-03 (3 min), 09-04 (6 min), 09-05 (3 min)
- Trend: All phases complete

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
- [07-01]: Monaco vs-dark theme for configuration editor (built-in, matches app aesthetic)
- [07-01]: Edit/Preview toggle in toolbar (not side-by-side split)
- [07-01]: Configuration hooks invalidate profile.effectiveConfiguration and profile.dashboard caches
- [07-02]: Timeline uses absolute positioned vertical line with circle indicators for active/inactive states
- [07-02]: isLatest determined by comparing version SHA with currentCommitSha prop
- [07-02]: Load more starts at 10, increments by 10 per click, shows "(N remaining)" count
- [07-02]: Empty state provides helpful guidance ("Save your configuration to create the first version")
- [07-03]: Zustand for draft state (simpler than Context, persists across tab switches)
- [07-03]: Import button in header toolbar alongside Save for quick access
- [07-03]: isDirty computed dynamically from content !== originalContent
- [07-04]: Version metadata display (message, author, date, SHA) since backend lacks historical content endpoint
- [07-04]: Confirmation dialog explains rollback creates new commit with old content
- [07-04]: Brief success state (1.5s) before navigating back to list
- [07-04]: Dirty warning dialog when clicking version with unsaved editor changes
- [07-05]: react-dropzone for drag-and-drop file upload (stable, well-maintained)
- [07-05]: Replace/Append merge dialog when importing with existing content
- [07-05]: Three badges (org/team/personal) with opacity for inactive sources
- [08-01]: Typer for CLI framework (simple, type-hint driven)
- [08-01]: Keyring for OS-native secure credential storage
- [08-01]: Atomic write pattern with temp file + rename for safety
- [08-01]: CLI module structure: commands/, api/, storage/
- [08-02]: httpx.Auth subclass for automatic token refresh on 401
- [08-02]: OAuth2 form data format for CLI login (matches backend)
- [08-02]: Dataclass config with environment variable overrides
- [08-03]: Content comparison before write to report "Already up to date"
- [08-03]: Truncated commit SHA (7 chars) for display readability
- [08-03]: Graceful handling of empty remote config (info message, not error)
- [08-04]: Doctor checks 5 areas: auth, config dir, config file, API connectivity, keyring backend
- [08-04]: Status compares local content with remote content for sync state
- [08-04]: Both doctor and status work gracefully without authentication
- [08-05]: ATLAS_ACCESS_TOKEN env var takes precedence over keyring for CI/headless systems
- [08-05]: Pytest pythonpath configured in pyproject.toml for src layout
- [08-05]: KeyringError caught gracefully with helpful error messages
- [09-01]: UserRole as StrEnum for string serialization and enum validation
- [09-01]: AuditLog frozen=True for immutable audit records
- [09-01]: JSON column for audit details to allow flexible before/after data
- [09-01]: is_admin property delegates to role check for clean API
- [09-01]: AuthorizationError exception class for authorization failures
- [09-02]: Fire-and-forget audit logging (try/except, log warning, don't fail request)
- [09-02]: Team deletion removes team from all users' team_ids
- [09-02]: 409 Conflict for duplicate team names and existing membership
- [09-02]: Bidirectional sync between team.member_ids and user.team_ids
- [09-03]: RequireAdmin dependency pattern for admin-only endpoints
- [09-03]: UserResponse excludes password_hash for security
- [09-03]: Fire-and-forget audit logging prevents main operation failure
- [09-03]: User email joined in audit logs for better visibility
- [09-04]: protectedLoader for admin routes; backend enforces admin role
- [09-04]: Role in auth /me endpoint for frontend admin detection
- [09-04]: Email confirmation pattern for user deletion
- [09-04]: Sheet component for team member management

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

## Phase 7 Completion Summary

All success criteria from ROADMAP.md are met:

1. User can edit claude.md configuration through web editor (07-01)
2. User can view version history of configuration changes (07-02)
3. User can rollback to any previous version (07-04)
4. User can import existing claude.md file (07-05)
5. Configuration inheritance is visible (org/team/user) (07-05)

Frontend Settings page:
- /settings - Configuration management with three tabs
  - Editor: Monaco markdown editor with preview toggle
  - History: Version timeline with rollback capability
  - Import: Drag-and-drop file upload with merge options
- Inheritance indicator shows which config levels apply
- Draft state persists across tab switches

## Phase 8 Completion Summary

All success criteria from ROADMAP.md are met:

1. CLI installs with single command (08-01)
2. User can authenticate via email/password (08-02)
3. User can sync configuration to ~/.claude/CLAUDE.md (08-03)
4. Sync uses atomic writes (no partial files on interrupt) (08-01, 08-03)
5. CLI shows helpful error messages (08-04, 08-05)

CLI commands:
- atlas auth login - authenticate with email/password
- atlas auth logout - clear credentials
- atlas auth status - show auth status
- atlas sync - sync config to local file
- atlas status - show sync status
- atlas doctor - health check diagnostics

CLI features:
- OS-native credential storage via keyring
- ATLAS_ACCESS_TOKEN env var for CI/headless systems
- Atomic writes prevent partial files
- 29 passing unit tests

## Phase 9 Completion Summary

All success criteria from ROADMAP.md are met:

1. Admin can view all users with role info (09-03, 09-04)
2. Admin can change user roles (09-03, 09-04)
3. Admin can create and manage teams (09-02, 09-04)
4. Admin can add/remove users from teams (09-02, 09-04)
5. All admin actions are audited (09-02, 09-03)

Admin API endpoints:
- GET/POST /api/v1/admin/teams - list/create teams
- GET/PUT/DELETE /api/v1/admin/teams/{id} - get/update/delete team
- POST/DELETE /api/v1/admin/teams/{id}/members - add/remove members
- GET /api/v1/admin/users - list users with search
- GET /api/v1/admin/users/{id} - get user
- PUT /api/v1/admin/users/{id}/role - change role
- DELETE /api/v1/admin/users/{id} - delete user

Admin frontend pages:
- /admin/teams - Team management with create/edit/delete
- /admin/users - User management with role change/delete
- Admin navigation visible only to admin users

## Session Continuity

Last session: 2026-01-25
Stopped at: Completed 09-04-PLAN.md (Phase 9 plan 4 - admin panel frontend)
Resume file: None
Next: All phases complete - project milestone finished!
