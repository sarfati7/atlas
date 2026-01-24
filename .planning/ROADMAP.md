# Roadmap: Atlas

## Overview

Atlas delivers an agent management platform enabling developers to discover company-wide skills, MCPs, and tools, then sync configurations to their local Claude instance. The journey moves from foundational data architecture (establishing the critical git=content, database=metadata separation) through backend APIs, frontend interfaces, CLI tooling, and finally governance features. Each phase delivers a complete, verifiable capability that builds toward the core value: a new developer can onboard in minutes instead of weeks.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation & Data Architecture** - PostgreSQL schema, Git integration, RBAC abstractions
- [x] **Phase 2: Authentication** - User accounts, sessions, password management
- [x] **Phase 3: Catalog Backend** - Skills/MCPs/tools API with search and filtering
- [x] **Phase 4: Configuration Backend** - Profile editing API with git-backed versioning
- [x] **Phase 5: User Profiles Backend** - Dashboard data and configuration inheritance
- [ ] **Phase 6: Web Frontend Core** - Authentication UI, catalog browser, profile dashboard
- [ ] **Phase 7: Web Frontend Configuration** - Profile editor, version history, import
- [ ] **Phase 8: CLI Sync Tool** - Atomic sync, authentication, cross-platform support
- [ ] **Phase 9: Governance & Admin** - Admin panel, audit logging, team management

## Phase Details

### Phase 1: Foundation & Data Architecture
**Goal**: Establish the foundational data layer with correct git/database separation and future-proof abstractions
**Depends on**: Nothing (first phase)
**Requirements**: INFR-01, INFR-02, INFR-03
**Success Criteria** (what must be TRUE):
  1. PostgreSQL database runs with SQLModel models for users, teams, skills, MCPs, tools
  2. Git repository integration fetches and commits skill/MCP/tool content files
  3. Webhooks or sync mechanism keeps database metadata in sync with git content
  4. Authorization abstraction layer exists (functions like `can_view_skill(user, skill)` even if returning True)
  5. Schema versioning strategy is in place with Alembic migrations
**Plans**: 5 plans

Plans:
- [x] 01-01-PLAN.md — Project setup and domain layer (entities, interfaces)
- [x] 01-02-PLAN.md — PostgreSQL SQLModel models and Alembic migrations
- [x] 01-03-PLAN.md — Repository implementations (PostgreSQL + in-memory)
- [x] 01-04-PLAN.md — GitHub content integration and authorization abstraction
- [x] 01-05-PLAN.md — Git-to-database sync mechanism (webhooks + manual sync)

### Phase 2: Authentication
**Goal**: Users can securely create accounts and manage their sessions
**Depends on**: Phase 1
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04
**Success Criteria** (what must be TRUE):
  1. User can create account with email and password
  2. User can log in and stay logged in across browser sessions (JWT/session persistence)
  3. User can log out from any page in the application
  4. User can reset forgotten password via email link
**Plans**: 3 plans

Plans:
- [x] 02-01-PLAN.md — Auth dependencies, domain layer (interfaces, value objects), JWT service, registration endpoint
- [x] 02-02-PLAN.md — Login, session management (access/refresh tokens), logout, /me endpoint
- [x] 02-03-PLAN.md — Password reset flow with email service (forgot-password, reset-password)

### Phase 3: Catalog Backend
**Goal**: Backend APIs serve complete skill/MCP/tool catalog with search and filtering
**Depends on**: Phase 1
**Requirements**: CATL-01, CATL-02, CATL-03, CATL-04, CATL-05, CATL-06
**Success Criteria** (what must be TRUE):
  1. API returns all skills available company-wide with metadata
  2. API returns all MCPs available company-wide with metadata
  3. API returns all tools available company-wide with metadata
  4. API supports keyword search across catalog items
  5. API supports filtering by type (skill/MCP/tool)
  6. Each catalog item includes documentation (description, usage examples)
**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md — Repository pagination + catalog list endpoint with search/filter
- [x] 03-02-PLAN.md — Catalog detail endpoint with documentation retrieval from git

### Phase 4: Configuration Backend
**Goal**: Backend APIs support profile editing with git-backed versioning and rollback
**Depends on**: Phase 1, Phase 2
**Requirements**: CONF-01, CONF-02, CONF-03, CONF-04, CONF-05
**Success Criteria** (what must be TRUE):
  1. API accepts and persists claude.md configuration edits
  2. All configuration changes are committed to git-backed repository
  3. API returns version history for user's configuration
  4. API supports rollback to any previous configuration version
  5. API accepts import of existing claude.md content
**Plans**: 3 plans

Plans:
- [x] 04-01-PLAN.md — Domain layer (entities, interfaces), DB model, migration, ContentRepository extension
- [x] 04-02-PLAN.md — Repository implementations (PostgreSQL, in-memory, GitHub/in-memory content extensions)
- [x] 04-03-PLAN.md — ConfigurationService, all REST endpoints, dependency injection

### Phase 5: User Profiles Backend
**Goal**: Backend APIs serve user dashboard data with configuration inheritance
**Depends on**: Phase 2, Phase 3, Phase 4
**Requirements**: PROF-01, PROF-02, PROF-03
**Success Criteria** (what must be TRUE):
  1. API returns user's personal dashboard data including their agent configuration
  2. API returns user's available skills, MCPs, and tools (their effective configuration)
  3. Configuration inheritance chain (org -> team -> user) is computed and returned
**Plans**: 2 plans

Plans:
- [x] 05-01-PLAN.md — Domain entity (EffectiveConfiguration) and UserProfileService with aggregation + inheritance
- [x] 05-02-PLAN.md — Profile REST endpoints (/dashboard, /available-items, /effective-configuration) and DI

### Phase 6: Web Frontend Core
**Goal**: Web UI enables authentication, catalog browsing, and profile viewing
**Depends on**: Phase 2, Phase 3, Phase 5
**Requirements**: (Frontend for AUTH-01, AUTH-02, AUTH-03, CATL-01 through CATL-06, PROF-01, PROF-02)
**Success Criteria** (what must be TRUE):
  1. User can sign up, log in, and log out through the web interface
  2. User can browse all skills, MCPs, and tools in a searchable catalog
  3. User can filter catalog by type and search by keyword
  4. User can view documentation for any catalog item
  5. User can view their personal dashboard showing their agent configuration
**Plans**: 5 plans

Plans:
- [ ] 06-01-PLAN.md — React project setup with Vite, TanStack Query, shadcn/ui, and dark theme
- [ ] 06-02-PLAN.md — Authentication pages (signup, login, logout, password reset) with forms
- [ ] 06-03-PLAN.md — Catalog browser with card layout, type filtering, and search
- [ ] 06-04-PLAN.md — Catalog item detail view with markdown documentation
- [ ] 06-05-PLAN.md — User dashboard with stats and configuration preview

### Phase 7: Web Frontend Configuration
**Goal**: Web UI enables profile editing with version history and import
**Depends on**: Phase 4, Phase 6
**Requirements**: (Frontend for CONF-01, CONF-03, CONF-04, CONF-05, PROF-03)
**Success Criteria** (what must be TRUE):
  1. User can edit their claude.md configuration through a web-based editor
  2. User can view version history of their configuration changes
  3. User can rollback to any previous configuration version
  4. User can import an existing claude.md file from their local machine
  5. Configuration inheritance is visible (what comes from org, team, user)
**Plans**: TBD

Plans:
- [ ] 07-01: Configuration editor component (claude.md editing)
- [ ] 07-02: Version history viewer with diff display
- [ ] 07-03: Rollback functionality
- [ ] 07-04: Import existing configuration upload
- [ ] 07-05: Inheritance visualization

### Phase 8: CLI Sync Tool
**Goal**: CLI tool syncs configuration from platform to local ~/.claude/ with reliability
**Depends on**: Phase 2, Phase 4
**Requirements**: SYNC-01, SYNC-02, SYNC-03
**Success Criteria** (what must be TRUE):
  1. CLI command syncs user's configuration to local `~/.claude/` directory
  2. CLI authenticates with user's Atlas account (stored securely in OS keychain)
  3. CLI pulls latest configuration from git repository
  4. Sync is atomic (no partial syncs on failure)
  5. CLI works on macOS, Linux, and Windows
**Plans**: TBD

Plans:
- [ ] 08-01: CLI project setup with Typer
- [ ] 08-02: Authentication flow and token storage
- [ ] 08-03: Sync command with atomic file operations
- [ ] 08-04: Status and doctor commands
- [ ] 08-05: Cross-platform testing and edge cases

### Phase 9: Governance & Admin
**Goal**: Admins can manage users, teams, and view audit logs
**Depends on**: Phase 1, Phase 2, Phase 6
**Requirements**: GOVR-01, GOVR-02, GOVR-03, GOVR-04, ADMN-01, ADMN-02, ADMN-03, ADMN-04
**Success Criteria** (what must be TRUE):
  1. Admin can create, edit, and delete teams through admin panel
  2. Admin can add and remove users from teams
  3. Admin can add and remove users from the platform
  4. Admin can view usage analytics (which tools used by whom)
  5. System logs all configuration changes (who, what, when)
  6. Admin can view audit logs of all changes
  7. User role has limited permissions (can only manage own profile)
**Plans**: TBD

Plans:
- [ ] 09-01: Team management backend and UI
- [ ] 09-02: User management backend and UI
- [ ] 09-03: Audit logging infrastructure
- [ ] 09-04: Usage analytics backend and dashboard
- [ ] 09-05: Role enforcement (admin vs user permissions)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Data Architecture | 5/5 | Complete | 2026-01-23 |
| 2. Authentication | 3/3 | Complete | 2026-01-23 |
| 3. Catalog Backend | 2/2 | Complete | 2026-01-24 |
| 4. Configuration Backend | 3/3 | Complete | 2026-01-24 |
| 5. User Profiles Backend | 2/2 | Complete | 2026-01-24 |
| 6. Web Frontend Core | 0/5 | Not started | - |
| 7. Web Frontend Configuration | 0/5 | Not started | - |
| 8. CLI Sync Tool | 0/5 | Not started | - |
| 9. Governance & Admin | 0/5 | Not started | - |

---
*Roadmap created: 2025-01-23*
*Total plans: 35*
*Total requirements: 32*
