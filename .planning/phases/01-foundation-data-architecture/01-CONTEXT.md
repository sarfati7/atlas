# Phase 1: Foundation & Data Architecture - Context

**Gathered:** 2025-01-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the foundational data layer with correct git/database separation. PostgreSQL stores metadata (users, teams, catalog item info, usage stats). Git repository stores actual content files (skills, MCPs, tools). Authorization abstraction exists even if permissive. Schema versioning with Alembic.

</domain>

<decisions>
## Implementation Decisions

### Data Model Design
- Users can belong to multiple teams (many-to-many relationship)
- Users have personal configuration layer that sits on top of team configurations
- Catalog items (skills/MCPs/tools) store in DB: name, description, author/owner, team association, tags/categories, usage stats
- Actual content files live in git, metadata lives in database

### Git Sync Mechanism
- Git repository hosted on GitHub
- Flat folder structure: `skills/`, `mcps/`, `tools/` with files directly inside
- When user creates/edits via web UI, changes push to git immediately (every save = git commit)

### Project Structure
- Monorepo: backend, frontend, CLI all in one repository
- Strict DDD/Clean Architecture layers per CLAUDE.md guidelines:
  - Domain layer (pure business logic, no I/O)
  - Application layer (orchestration, use cases)
  - Adapters layer (database, git, external integrations)
  - Entrypoints layer (HTTP routes, CLI commands)
- Frontend uses npm as package manager

### Claude's Discretion
- Catalog item entity design: separate tables vs single table with type field
- Git sync mechanism: webhooks vs polling vs manual trigger
- Python package manager choice (uv, Poetry, or pip)
- Authorization abstraction API design

</decisions>

<specifics>
## Specific Ideas

- Configuration inheritance: org → team → user layers, where user's personal config overrides team defaults
- Every interface needs two implementations per CLAUDE.md: real (PostgreSQL, GitHub) and test (in-memory)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation-data-architecture*
*Context gathered: 2025-01-23*
