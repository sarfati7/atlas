# Project Research Summary

**Project:** Atlas Agent Management Platform
**Domain:** AI Agent Configuration and Tools Management
**Researched:** 2026-01-23
**Confidence:** MEDIUM-HIGH

## Executive Summary

Atlas is an agent management platform designed to solve the "weeks to productive" problem that enterprise developers face when setting up AI coding assistants like Claude Code. The research reveals this is fundamentally a developer portal (IDP) focused specifically on AI agent configuration, bridging the gap between centralized tool catalogs and local developer environments through a git-backed architecture.

The recommended approach combines a React web UI for browsing and configuration with a Python FastAPI backend that serves dual purposes: REST API for humans and MCP protocol for AI agents. Git serves as the single source of truth for content (skills, MCPs, tools), while PostgreSQL stores queryable metadata and user relationships. A lightweight CLI tool syncs configurations from Git to local ~/.claude/ directories, giving developers control over when changes apply.

The critical risk is the "git-as-database trap" — using git for queries and relationships when a database is essential. This mistake has killed similar platforms at scale. The mitigation is straightforward but must be implemented from day one: git stores only file content, database stores all metadata and relationships, webhooks keep them in sync. Secondary risks include MCP security theater (treating internal MCP servers as trusted) and CLI sync corruption (partial syncs, file conflicts). Both require defensive design from the start, not retrofits.

## Key Findings

### Recommended Stack

The research strongly favors modern, high-performance tools with active ecosystems. React 19.2 provides the latest stable frontend capabilities. FastAPI 0.128.0 is 6x faster than Django and ideal for AI-driven applications with native async support and automatic OpenAPI documentation. SQLModel bridges FastAPI and PostgreSQL cleanly, reducing boilerplate while maintaining full SQLAlchemy power for complex queries.

**Core technologies:**
- **React 19.2 + Vite 7.3.1**: Modern frontend with fast builds (100x faster incremental than alternatives)
- **FastAPI 0.128.0 + Python 3.12+**: High-performance async API with automatic validation and docs
- **PostgreSQL 16+**: Robust database with JSON support, full-text search, and excellent concurrency
- **SQLModel 0.0.31**: FastAPI-native ORM combining SQLAlchemy power with Pydantic validation
- **TanStack Query 5.90+**: De facto standard for server state management, handles 80% of data fetching patterns
- **Zustand 5.0**: Lightweight client state (40% adoption in 2025), perfect complement to TanStack Query
- **shadcn/ui**: Copy-paste components with full control, no lock-in (100k+ stars)
- **MCP Python SDK 1.25.0**: Official Anthropic SDK, stick to v1.x stable (v2 expected Q1 2026)
- **Typer 0.21.1**: FastAPI-style CLI framework with rich terminal output

**Critical version notes:**
- Avoid CRA (deprecated Feb 2025), use Vite
- Avoid Tailwind v3, use v4 (100x faster incremental builds)
- Avoid MCP SDK v2 beta (not stable yet)
- Use asyncpg 0.31.0 for 5x faster PostgreSQL performance

### Expected Features

Research identifies a clear three-tier feature hierarchy. MVP focuses on the core value proposition: centralized discovery with web-based configuration and CLI sync. Post-MVP adds team collaboration and governance. Future phases tackle analytics and cross-platform support.

**Must have (table stakes):**
- Centralized catalog/registry for skills, MCPs, and tools
- Web UI for visual configuration (no hand-editing YAML/markdown)
- CLI sync tool (one-way: platform to local)
- User authentication with SSO (enterprise requirement)
- Basic search and filtering
- Git integration for version control
- Documentation for each tool/skill

**Should have (competitive advantage):**
- Minutes-to-productive onboarding (core differentiator vs weeks-long IDP setup)
- Team-curated tool packs (role-based bundles: Frontend Pack, Data Science Pack)
- Configuration inheritance (org > team > user with overrides)
- Version history and rollback (git makes this natural)
- Import from existing claude.md (migration path)
- Usage analytics (which tools are actually valuable)

**Defer (v2+):**
- Smart recommendations (requires ML and usage data)
- Tool/MCP health monitoring (requires ecosystem integration)
- Approval workflows (enterprise governance)
- Private MCP registry (enterprise security)
- Cross-agent support (Cursor, GitHub Copilot, etc.)

**Anti-features to avoid:**
- Real-time sync (creates conflicts; use pull-based)
- In-platform agent execution (scope creep)
- Marketplace with payments (premature complexity)
- AI-generated configurations (low quality without curation)

### Architecture Approach

The architecture is a hybrid: Git stores content, database stores metadata. This separation is critical — it appears in both ARCHITECTURE.md and PITFALLS.md as the most important architectural decision. The system has five major components that communicate through well-defined boundaries.

**Major components:**
1. **React Frontend** — Web UI for browsing skills/MCPs/tools, editing agent profiles, team management (React + TypeScript + Vite + shadcn/ui)
2. **Python MCP Server** — Dual-mode API: REST for web UI, MCP protocol for AI agents; handles business logic, Git operations, authentication (FastAPI + MCP SDK + GitPython)
3. **PostgreSQL Database** — Metadata storage: user profiles, team structure, permissions, audit logs, searchable skill/MCP metadata (PostgreSQL 16+ with SQLModel)
4. **Git Repository** — Single source of truth for skill/MCP/tool file content, provides version control and collaboration (GitHub/GitLab)
5. **CLI Tool** — Local synchronization from Git to ~/.claude/ directories, handles authentication and file management (Typer + asyncio)

**Key patterns:**
- **Git as source of truth, database as index:** Never query Git for data. Webhooks sync content changes to database metadata.
- **Unified service layer:** Same business logic serves both MCP and REST endpoints
- **Pull-based CLI:** CLI pulls directly from Git (not through backend API) for offline capability and Git-native conflict resolution
- **Separation of concerns:** API layer → Service layer → Infrastructure layer with async I/O

**Data flow:**
- Browse: User → React → FastAPI (queries PostgreSQL metadata) → Git (fetches content) → React
- Edit: User → React → FastAPI (commits to Git) → Webhook → FastAPI (syncs metadata to PostgreSQL)
- Sync: Developer → CLI (fetches profile from FastAPI) → Git (pulls content) → Local ~/.claude/

### Critical Pitfalls

Research reveals six critical pitfalls that have killed similar platforms. Each requires preventive design decisions in specific phases — retrofitting is expensive or impossible.

1. **Git-as-Database Trap** — Using git for queries/relationships instead of database. Leads to slow queries, custom indexing, merge conflicts in metadata. Prevention: Git stores only file content, PostgreSQL stores all metadata and relationships, webhooks keep in sync. Address in Phase 1 (Data Architecture).

2. **MCP Security Theater** — Treating company MCPs as trusted. 2025 breaches (GitHub MCP exfiltration, Anthropic Inspector RCE) prove this wrong. Prevention: Explicit user consent for all tool invocations, never auto-execute, validate server identity, scope tokens per server (RFC 8707). Address in Phase 2 (MCP Integration).

3. **CLI Sync State Corruption** — Partial syncs, network failures, file conflicts, platform differences (case sensitivity, path limits). Prevention: Atomic operations (write to temp, then move), checksums to detect drift, `atlas status` and `atlas doctor` commands, never silently overwrite user changes. Address in Phase 3 (CLI Development).

4. **All-Admin-Now, RBAC-Later Disaster** — Starting with "all users are admins" to simplify v1, discovering RBAC can't be retrofitted without breaking changes. Prevention: Abstract authorization from day one with `can_view_skill(user, skill)` functions (even if they return True), design database schema with ownership/team fields. Address in Phase 1 (Data Architecture).

5. **Agent Profile Versioning Neglect** — No rollback when agent configs break. Prevention: Store all profile versions, tie to git commits, show diffs, allow instant rollback. Address in Phase 2 (Profile Management).

6. **Schema Migration Amnesia** — Skills/MCPs/tools schemas evolve, old formats accumulate. Prevention: Version schemas explicitly, write migrations, validate on import with clear errors. Address in Phase 1 (Data Architecture).

## Implications for Roadmap

Based on combined research, the architecture dependency graph and pitfall timing dictate a clear phase structure. The git/database boundary must be established before any code. MCP and CLI come after the content system is stable. Analytics and governance are post-MVP enhancements.

### Phase 1: Data Architecture & Foundation
**Rationale:** Everything depends on correct database schema and git/database separation. The "git-as-database trap" and "RBAC retrofit disaster" must be prevented here — retrofitting either is catastrophic. Schema versioning must be built in from day one.

**Delivers:** PostgreSQL schema with SQLModel models, Git integration service layer, abstract authorization layer (even if policy is "allow all"), schema versioning strategy, database migrations with Alembic.

**Addresses (from FEATURES.md):** Foundation for centralized catalog, git integration for version control

**Avoids (from PITFALLS.md):** Git-as-database trap (explicit git=content, database=metadata separation), All-admin RBAC disaster (permission abstractions from start), Schema migration amnesia (version field in all schemas)

**Implements (from ARCHITECTURE.md):** PostgreSQL database component, Git service layer, data model for users/teams/skills metadata

**Research flag:** Standard patterns (skip research-phase) — PostgreSQL schema design and SQLAlchemy patterns are well-documented

### Phase 2: REST API & MCP Integration
**Rationale:** Once data layer is solid, build dual-mode API. MCP protocol must include security controls from the start (not bolted on). Profile versioning must be in the data model, not added later.

**Delivers:** FastAPI REST endpoints for skills/profiles/teams, MCP protocol handlers with consent flows, unified service layer serving both APIs, profile versioning with rollback, JWT authentication with SSO support

**Addresses (from FEATURES.md):** User authentication (SSO), centralized catalog API access

**Avoids (from PITFALLS.md):** MCP security theater (explicit consent flows, token scoping), Profile versioning neglect (versions stored from start)

**Implements (from ARCHITECTURE.md):** MCP Server component with dual REST/MCP interface, authentication layer

**Research flag:** Needs research-phase — MCP security patterns are evolving (2025 breaches inform best practices), SSO integration patterns vary by provider

### Phase 3: Web Frontend
**Rationale:** Build on stable API. Frontend consumes REST endpoints for browsing, configuration, and team management. Must include pagination from day one to avoid performance traps.

**Delivers:** React UI with skill browser, profile editor, team dashboard, search with pagination, version history view, basic RBAC UI

**Addresses (from FEATURES.md):** Web UI for configuration, basic search, user profiles, documentation display

**Avoids (from PITFALLS.md):** Performance traps (pagination and virtual scrolling from v1), UX pitfalls (validation before save, clear error states)

**Implements (from ARCHITECTURE.md):** React Frontend component

**Research flag:** Standard patterns (skip research-phase) — React + TanStack Query + shadcn/ui have established patterns

### Phase 4: CLI Sync Tool
**Rationale:** CLI is the bridge to local development. Requires backend API and Git content to be stable. Must handle platform differences (Windows/macOS/Linux) and sync corruption from the start.

**Delivers:** CLI tool with `sync`, `status`, `doctor` commands, atomic sync operations with checksums, authentication token management (OS keychain), cross-platform testing

**Addresses (from FEATURES.md):** CLI sync tool (core table stake), import from existing (migration path)

**Avoids (from PITFALLS.md):** CLI sync corruption (atomic operations, checksums, rollback), Security mistakes (keychain storage, no plaintext credentials)

**Implements (from ARCHITECTURE.md):** CLI Tool component, pull-based Git synchronization

**Research flag:** Needs research-phase — Cross-platform file handling has subtle gotchas (case sensitivity, path limits, symlinks)

### Phase 5: Team Features & Governance
**Rationale:** Post-MVP. Builds on existing RBAC abstractions (which were added in Phase 1). Adds team collaboration features that differentiate Atlas from simple tool catalogs.

**Delivers:** Team-curated tool packs, configuration inheritance (org > team > user), approval workflows, audit logging, team management UI

**Addresses (from FEATURES.md):** Team-curated tool packs (competitive advantage), configuration inheritance, approval workflows, audit logging

**Avoids (from PITFALLS.md):** Uses RBAC abstractions created in Phase 1 (no retrofit needed)

**Implements (from ARCHITECTURE.md):** Team boundaries, approval workflow integration points

**Research flag:** Standard patterns (skip research-phase) — RBAC and audit logging are well-established patterns

### Phase 6: Analytics & Advanced Features
**Rationale:** Future work. Requires usage data from production. ML-based recommendations need training data from actual user behavior.

**Delivers:** Usage analytics dashboard, smart recommendations, tool/MCP health monitoring, private MCP registry

**Addresses (from FEATURES.md):** Usage analytics, smart recommendations, health monitoring, private MCP registry

**Implements (from ARCHITECTURE.md):** Analytics layer, recommendation engine, health monitoring service

**Research flag:** Needs research-phase — ML recommendation systems and health monitoring require domain-specific patterns

### Phase Ordering Rationale

- **Data first, always:** Phase 1 establishes git/database separation and RBAC abstractions. These are load-bearing architectural decisions that can't be changed later without massive rework.
- **Dual API before consumption:** Phase 2 builds both REST and MCP interfaces. Phase 3 (frontend) and Phase 4 (CLI) consume these stable APIs.
- **Frontend before CLI:** Phase 3 provides immediate value (web browsing) and validates API design. Phase 4 CLI depends on API stability.
- **Team features after MVP:** Phase 5 uses RBAC abstractions from Phase 1 but defers to post-MVP because solo developers get value without team features.
- **Analytics last:** Phase 6 requires production usage data. Can't build recommendations before users exist.

**Dependency validation:**
- Phase 3 (Frontend) depends on Phase 2 (API) — REST endpoints must exist
- Phase 4 (CLI) depends on Phase 2 (API) — Auth and profile endpoints must exist
- Phase 5 (Teams) depends on Phase 1 (Data) — RBAC abstractions must exist
- Phase 6 (Analytics) depends on Phase 5 (Teams) — Usage data requires audit logging

### Research Flags

**Phases likely needing deeper research during planning:**
- **Phase 2 (MCP Integration):** MCP security patterns are still evolving post-2025 breaches. Need specific research on consent flows, token scoping (RFC 8707), and server identity verification.
- **Phase 4 (CLI Development):** Cross-platform file handling has subtle gotchas. Research needed on Windows path limits, case sensitivity handling, atomic file operations across platforms.
- **Phase 6 (Analytics & ML):** ML recommendation systems need domain-specific research. Health monitoring patterns for MCP servers are niche.

**Phases with standard patterns (skip research-phase):**
- **Phase 1 (Data Architecture):** PostgreSQL + SQLAlchemy patterns are well-documented. FastAPI full-stack template provides reference.
- **Phase 3 (Frontend):** React + TanStack Query + shadcn/ui have established patterns. Browsing/CRUD UIs are standard.
- **Phase 5 (Team Features):** RBAC and audit logging are well-established. Backstage and similar IDPs provide reference architectures.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Official docs and version info verified. FastAPI + React + PostgreSQL is proven combination. MCP SDK versions confirmed. |
| Features | MEDIUM | Based on WebSearch across multiple IDP platforms, MCP ecosystem, and enterprise AI governance sources. Feature dependencies validated against Backstage/Port.io patterns. |
| Architecture | MEDIUM-HIGH | MCP architecture from official spec (HIGH). Git-as-source-of-truth from GitOps patterns (MEDIUM). Fullstack patterns from FastAPI template and IDP references (MEDIUM-HIGH). |
| Pitfalls | MEDIUM-HIGH | Critical pitfalls (git-as-database, MCP security) verified with multiple sources including 2025 breach timelines. Some performance trap claims from single benchmarks (MEDIUM). |

**Overall confidence:** MEDIUM-HIGH

The stack recommendations are rock-solid (official sources, current versions). The architecture approach combines proven patterns (GitOps, IDP architecture) with MCP-specific design (official spec). Feature prioritization is informed by competitor analysis but lacks direct user research. Pitfall identification benefits from real-world failures (2025 MCP breaches, git-as-database antipatterns) but some performance claims need production validation.

### Gaps to Address

**During Phase 1 (Data Architecture):**
- Validate schema design with security review focusing on RBAC abstractions
- Confirm git webhook reliability under production load (what happens if webhook fails?)
- Decide on specific SSO provider to design auth layer around

**During Phase 2 (MCP Integration):**
- Deep research on MCP consent flow UX patterns (how do other platforms handle this?)
- Validate token scoping approach with RFC 8707 Resource Indicators implementation
- Test MCP protocol with multiple client types (not just Claude Code)

**During Phase 4 (CLI Development):**
- Cross-platform testing on actual Windows/macOS/Linux machines, not just CI
- Validate `~/.claude/` directory structure expectations with Claude Code docs
- Research OS keychain APIs across platforms (macOS Keychain, Windows Credential Manager, Linux Secret Service)

**During Phase 6 (Analytics & ML):**
- Research recommendation algorithms for developer tools (different from e-commerce recommendations)
- Investigate health monitoring patterns for distributed MCP servers
- Validate analytics privacy requirements (PII in tool usage logs?)

## Sources

### Primary (HIGH confidence)
- **STACK.md sources:** React official docs, FastAPI release notes, Vite releases, TanStack Query npm, MCP Python SDK GitHub, Pydantic releases, SQLModel GitHub
- **ARCHITECTURE.md sources:** MCP Architecture Specification (official), MCP Architecture Design Philosophy, FastAPI Full-Stack Template (official)
- **PITFALLS.md sources:** MCP Specification 2025-11-25 (official), AuthZed Timeline of MCP Breaches, Red Hat MCP Security Risks

### Secondary (MEDIUM confidence)
- **FEATURES.md sources:** MCP Registry Official, MCP Enterprise Adoption Guide 2025, Backstage vs IDP Comparison 2025, Microsoft AI Agent Governance, Composio AI Agent Management Guide
- **ARCHITECTURE.md sources:** InfoQ Multi-Agent Design Patterns, Speakeasy MCP Architecture Patterns, GitOps in 2025 (CNCF), CrafterCMS Git-Based CMS Advantages
- **PITFALLS.md sources:** Composio 2025 AI Agent Report, McKinsey One Year of Agentic AI, Auth0 MCP Specs Update, JetBrains Configuration Drift, Idenhaus RBAC Implementation Pitfalls

### Tertiary (LOW confidence, needs validation)
- asyncpg 5x faster than psycopg3 (2023 benchmark, may be outdated)
- Prisma Python 3x faster introspection (single source benchmark)
- Some performance trap breakpoints ("> 200 skills") are estimates, not measured

---
*Research completed: 2026-01-23*
*Ready for roadmap: yes*
