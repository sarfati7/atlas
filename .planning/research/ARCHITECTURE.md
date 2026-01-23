# Architecture Research

**Domain:** Agent Management Platform
**Researched:** 2026-01-23
**Confidence:** MEDIUM-HIGH

## Standard Architecture

Atlas is an agent management platform combining several components: web frontend, MCP server backend, PostgreSQL database, Git repository, and CLI. This represents a hybrid architecture where Git serves as the source of truth for actual content files while the database holds metadata, user profiles, and team structure.

### System Overview

```
                                    +-----------------------+
                                    |    External Services  |
                                    | (Monday, Slack, Docs) |
                                    +-----------+-----------+
                                                |
+-------------------------------------------------------------------------------------------+
|                                        ATLAS SYSTEM                                        |
|                                                                                           |
|   +-------------------+      +----------------------+      +-------------------+          |
|   |   React Frontend  |      |   Python MCP Server  |      |   Git Repository  |          |
|   |   (Web Browser)   |<---->|   (Backend/API)      |<---->|  (Source of Truth)|          |
|   +-------------------+      +----------+-----------+      +-------------------+          |
|          |                              |                           ^                     |
|          |                              |                           |                     |
|          |                   +----------v-----------+               |                     |
|          |                   |  PostgreSQL Database |               |                     |
|          |                   |    (Metadata Store)  |               |                     |
|          |                   +----------------------+               |                     |
|          |                                                          |                     |
|   +------v-------------+                                            |                     |
|   |    Developer's     |      +----------------------+              |                     |
|   |    Local Machine   |<---->|     CLI Tool         +--------------+                     |
|   | (~/.claude/ files) |      | (atlas-cli / sync)   |                                    |
|   +--------------------+      +----------------------+                                    |
|                                                                                           |
+-------------------------------------------------------------------------------------------+
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **React Frontend** | User interface for browsing skills/MCPs/tools, editing agent profiles, team management | React + TypeScript + Vite + shadcn/ui |
| **Python MCP Server** | API layer, MCP protocol handling, business logic, Git operations, authentication | FastAPI + MCP SDK + GitPython |
| **PostgreSQL Database** | Metadata storage, user profiles, team structure, permissions, audit logs | PostgreSQL 15+ with SQLAlchemy/SQLModel |
| **Git Repository** | Source of truth for skill/MCP/tool files, version control, collaboration | GitHub/GitLab hosted repo |
| **CLI Tool** | Local synchronization, file management, authentication | Click + asyncio + git operations |

## Recommended Project Structure

```
atlas/
├── frontend/                   # React web application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route-based page components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API client, data fetching
│   │   ├── stores/             # State management (Zustand/Jotai)
│   │   ├── types/              # TypeScript types
│   │   └── utils/              # Helper functions
│   ├── public/
│   └── package.json
│
├── backend/                    # Python MCP server
│   ├── src/
│   │   ├── api/                # FastAPI routes
│   │   │   ├── v1/             # API version 1
│   │   │   └── mcp/            # MCP-specific endpoints
│   │   ├── core/               # Business logic
│   │   ├── models/             # SQLModel/SQLAlchemy models
│   │   ├── services/           # Domain services (git, sync)
│   │   ├── mcp/                # MCP protocol handlers
│   │   └── integrations/       # External service connectors
│   ├── alembic/                # Database migrations
│   ├── tests/
│   └── pyproject.toml
│
├── cli/                        # CLI tool
│   ├── src/
│   │   ├── commands/           # Click command groups
│   │   ├── sync/               # Synchronization logic
│   │   ├── config/             # CLI configuration
│   │   └── utils/              # Helper functions
│   ├── tests/
│   └── pyproject.toml
│
├── shared/                     # Shared schemas/types (optional)
│   ├── schemas/                # JSON schemas for validation
│   └── types/                  # Shared type definitions
│
├── docker-compose.yml          # Local development setup
├── docker-compose.prod.yml     # Production deployment
└── .github/                    # CI/CD workflows
```

### Structure Rationale

- **frontend/:** Separated to allow independent development cycles, different build tooling, and potential deployment to CDN
- **backend/:** Contains all server-side logic with clear separation between API layer, business logic, and infrastructure
- **cli/:** Independent package that can be distributed via pip, operates offline after sync
- **shared/:** Optional layer for JSON schemas that both frontend and backend validate against

## Architectural Patterns

### Pattern 1: Git as Source of Truth with Database Metadata

**What:** Store actual skill/MCP/tool files in Git, store searchable metadata in PostgreSQL
**When to use:** When content needs version control, collaboration, and DevOps workflows
**Trade-offs:**
- Pro: Full version history, branching/merging, offline capability
- Pro: Fast metadata queries without parsing files
- Con: Must keep metadata in sync with Git content
- Con: Two sources that can diverge

**Example:**
```python
# When a skill file is modified in Git:

# 1. Git webhook triggers backend
@router.post("/webhooks/git")
async def handle_git_webhook(payload: GitWebhookPayload):
    changed_files = payload.commits.get_changed_files()
    for file_path in changed_files:
        if file_path.endswith('.md') and 'skills/' in file_path:
            await sync_skill_metadata(file_path, payload.repository)

# 2. Parse file and update metadata
async def sync_skill_metadata(file_path: str, repo: str):
    content = await git_service.get_file_content(repo, file_path)
    skill_meta = parse_skill_frontmatter(content)

    await db.execute(
        insert(SkillMetadata)
        .values(
            path=file_path,
            name=skill_meta.name,
            description=skill_meta.description,
            tags=skill_meta.tags,
            updated_at=datetime.utcnow()
        )
        .on_conflict_do_update(...)
    )
```

### Pattern 2: MCP Server as API Gateway

**What:** Use MCP protocol for AI agent communication, REST API for web frontend
**When to use:** When supporting both Claude/AI clients and human users via web UI
**Trade-offs:**
- Pro: Native MCP support for AI tools
- Pro: Same business logic serves both interfaces
- Con: Must maintain two API styles

**Example:**
```python
# Unified service layer used by both MCP and REST

class SkillService:
    async def get_skill(self, skill_id: str) -> Skill:
        # Business logic shared between MCP and REST
        skill_meta = await self.db.get(SkillMetadata, skill_id)
        skill_content = await self.git.get_file(skill_meta.path)
        return Skill.from_meta_and_content(skill_meta, skill_content)

# MCP handler
@mcp_server.tool("get_skill")
async def mcp_get_skill(skill_id: str):
    return await skill_service.get_skill(skill_id)

# REST handler
@router.get("/api/v1/skills/{skill_id}")
async def rest_get_skill(skill_id: str):
    return await skill_service.get_skill(skill_id)
```

### Pattern 3: Pull-Based CLI Synchronization

**What:** CLI pulls from Git repository, not from the backend API
**When to use:** When Git is the source of truth and you want offline capability
**Trade-offs:**
- Pro: Works offline after initial clone
- Pro: Git handles conflict resolution
- Pro: Users can customize before sync
- Con: CLI must understand file formats
- Con: Backend doesn't know what user has locally

**Example:**
```python
# CLI sync command
@click.command()
@click.option('--profile', default='default')
def sync(profile: str):
    """Sync agent configuration from Git to local ~/.claude/"""

    # 1. Get user's agent profile from backend (defines what to sync)
    profile_config = api_client.get_profile(profile)

    # 2. Clone/pull from Git repository
    repo = git_ops.ensure_repo(profile_config.repo_url)
    repo.pull()

    # 3. Copy selected files to local
    for skill in profile_config.enabled_skills:
        src = repo.path / 'skills' / skill.path
        dst = Path.home() / '.claude' / 'skills' / skill.filename
        shutil.copy(src, dst)

    click.echo(f"Synced {len(profile_config.enabled_skills)} skills")
```

## Data Flow

### Request Flow: Web UI Browsing Skills

```
User (Browser)
    |
    v
[React Frontend]
    | HTTP GET /api/v1/skills?tag=coding
    v
[MCP Server / FastAPI]
    |
    +---> [PostgreSQL] Query metadata (fast lookup)
    |        SELECT * FROM skills WHERE tags @> '{"coding"}'
    |
    +---> [Git Service] Fetch file content (on-demand)
    |        git show main:skills/coding-assistant.md
    v
[Response: Skill list with content previews]
    |
    v
[React Frontend]
    | Render skill cards
    v
User sees skill browser
```

### Request Flow: CLI Sync

```
Developer (Terminal)
    | atlas sync --profile work
    v
[CLI Tool]
    | HTTP GET /api/v1/profiles/work
    v
[MCP Server / FastAPI]
    | Query profile configuration
    v
[PostgreSQL]
    | Returns: enabled_skills, repo_url, last_sync
    v
[CLI Tool]
    | git clone/pull repo_url
    v
[Git Repository]
    | Clone/pull files
    v
[CLI Tool]
    | Copy files to ~/.claude/
    v
[Local File System]
    | skills/, mcps/, tools/ updated
    v
Developer ready to use updated agent config
```

### State Management

```
[Git Repository] <-- Single source of truth for CONTENT
    |
    | Webhooks on push
    v
[MCP Server] <-- Sync metadata on Git changes
    |
    | CRUD operations
    v
[PostgreSQL] <-- Queryable METADATA (derived from Git)
    |
    | Read for UI queries
    v
[React Frontend] <-- Display state
    |
    | User edits (optional web editor)
    v
[MCP Server] <-- Commit changes to Git
    |
    v
[Git Repository] <-- Circle complete
```

### Key Data Flows

1. **Browse -> Display:** User browses skills in web UI. Frontend queries backend metadata, backend fetches content from Git on-demand.
2. **Edit -> Save:** User edits skill in web UI. Backend commits to Git, webhook triggers metadata re-sync.
3. **Sync -> Local:** Developer runs CLI sync. CLI fetches profile config, pulls from Git, copies to local.
4. **MCP -> AI:** Claude Code queries available tools. MCP server returns tool definitions from metadata.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users | Monolith is fine. Single PostgreSQL, single MCP server instance. Git operations inline. |
| 1k-100k users | Add Redis cache for metadata queries. Queue Git operations (webhook processing). Consider read replicas for PostgreSQL. |
| 100k+ users | Separate MCP server from REST API. Git operation workers. Consider CDN for static skill content. PostgreSQL sharding by tenant. |

### Scaling Priorities

1. **First bottleneck: Git operations** - Git clone/pull for each user request is slow. Solution: Cache cloned repos, use shallow clones, implement Git proxy layer.
2. **Second bottleneck: Metadata queries** - Frequent skill searches hit database. Solution: Redis cache for hot queries, Elasticsearch for full-text search.
3. **Third bottleneck: Webhook processing** - Many pushes can overwhelm sync. Solution: Queue-based processing with workers (Celery/RQ).

## Anti-Patterns

### Anti-Pattern 1: Database as Primary Content Store

**What people do:** Store skill file content directly in PostgreSQL instead of Git
**Why it's wrong:** Lose version control, branching, collaboration features. Difficult migrations. Lock-in.
**Do this instead:** Use Git as source of truth for content. Database only for queryable metadata.

### Anti-Pattern 2: CLI Syncs from API Instead of Git

**What people do:** CLI fetches file content through the backend API
**Why it's wrong:** Couples CLI to backend availability. No offline mode. Backend becomes bottleneck.
**Do this instead:** CLI pulls directly from Git. Backend only provides profile configuration.

### Anti-Pattern 3: Tight Coupling Between Metadata and Content

**What people do:** Duplicate all content fields in metadata. Parse/store full content in database.
**Why it's wrong:** Hard to keep in sync. Database bloat. Parsing errors corrupt data.
**Do this instead:** Store only queryable fields (name, tags, description) in metadata. Fetch full content from Git on-demand.

### Anti-Pattern 4: Monolithic MCP Server

**What people do:** Put MCP protocol handling, REST API, Git operations, and integrations in one tightly coupled module
**Why it's wrong:** Hard to test, hard to scale components independently, risk of blocking MCP calls with slow Git operations
**Do this instead:** Layer properly: API layer -> Service layer -> Infrastructure layer. Use async for I/O operations.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **GitHub/GitLab** | Webhooks + API | Webhooks for push events, API for file operations. Use App/OAuth for auth. |
| **Monday** | REST API polling or webhooks | Future: Pull context for task-aware agent initialization |
| **Slack** | Events API + Web API | Future: Notifications, channel context for agents |
| **Docs (Confluence/Notion)** | REST API | Future: Pull documentation context |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Frontend <-> Backend | REST API (JSON) | OpenAPI spec, typed client generation |
| Backend <-> Git | Git protocol + API | GitPython for local ops, API for remote ops |
| Backend <-> Database | SQL via ORM | SQLModel/SQLAlchemy with Alembic migrations |
| CLI <-> Backend | REST API (subset) | Auth token, profile config only |
| CLI <-> Git | Git protocol | Direct clone/pull, no backend involvement |
| MCP Clients <-> Backend | MCP Protocol (JSON-RPC) | Stateful sessions, capability negotiation |

## Build Order Recommendations

Based on component dependencies, the recommended build order:

### Phase 1: Foundation (Must build first)

1. **PostgreSQL Schema** - Define core models (users, teams, skills metadata, profiles)
2. **Backend Core** - FastAPI skeleton with auth, basic CRUD for metadata
3. **Git Integration** - Service layer for Git operations (clone, pull, read file)

*Rationale:* Everything depends on the database schema and backend services. Can't build frontend without API. Can't build CLI without auth and profile endpoints.

### Phase 2: Primary Interfaces

4. **REST API** - Full API for skills, profiles, teams
5. **React Frontend** - Skill browser, profile editor, team management
6. **Webhook Handler** - Git push webhook to trigger metadata sync

*Rationale:* Frontend needs stable API. Webhook sync keeps metadata fresh.

### Phase 3: Distribution

7. **CLI Tool** - Auth, profile fetch, Git sync to local
8. **MCP Protocol** - MCP server implementation for AI clients

*Rationale:* CLI and MCP are consumption interfaces. Can be built after content and API are stable.

### Phase 4: Enhancements

9. **Integrations** - Monday, Slack, Docs connectors
10. **Advanced Features** - Search, analytics, team permissions

*Rationale:* These extend core functionality but aren't critical for MVP.

### Dependency Graph

```
[PostgreSQL Schema]
        |
        v
[Backend Core] -----> [Git Integration]
        |                    |
        v                    v
[REST API] <----------[Webhook Handler]
        |
        +-------+-------+
        |       |       |
        v       v       v
[Frontend]  [CLI]  [MCP Server]
                        |
                        v
                 [Integrations]
```

## Sources

### MCP Architecture (HIGH confidence)
- [Model Context Protocol Architecture Specification](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [MCP Architecture: Design Philosophy & Engineering Principles](https://modelcontextprotocol.info/docs/concepts/architecture/)
- [Kubiya: MCP Architecture Components & Workflow](https://www.kubiya.ai/blog/model-context-protocol-mcp-architecture-components-and-workflow)

### Agent Platform Patterns (MEDIUM confidence)
- [InfoQ: Google's Multi-Agent Design Patterns](https://www.infoq.com/news/2026/01/multi-agent-design-patterns/)
- [Speakeasy: Architecture Patterns for Agentic Applications](https://www.speakeasy.com/mcp/using-mcp/ai-agents/architecture-patterns)
- [Salesforce: Enterprise Agentic Architecture](https://architect.salesforce.com/fundamentals/enterprise-agentic-architecture)

### Git as Source of Truth (MEDIUM confidence)
- [GitOps in 2025 (CNCF)](https://www.cncf.io/blog/2025/06/09/gitops-in-2025-from-old-school-updates-to-the-modern-way/)
- [CrafterCMS: Git-Based Headless CMS Advantages](https://craftercms.com/blog/2022/04/advantages-of-a-git-based-headless-cms)
- [Simple Talk: Git-Based vs API-Based CMS](https://www.red-gate.com/simple-talk/development/web/headless-cms-content-management-systems-contrasting-git-based-and-api-based/)

### Fullstack Architecture (MEDIUM confidence)
- [FastAPI Full-Stack Template (Official)](https://github.com/fastapi/full-stack-fastapi-template)
- [InfoWorld: Separating Metadata and Content](https://www.infoworld.com/article/4092063/building-a-scalable-document-management-system-lessons-from-separating-metadata-and-content.html)
- [Clean Architecture with Dependency Rule](https://medium.com/design-microservices-architecture-with-patterns/clean-architecture-with-dependency-rule-dff96d479a60)

### CLI Patterns (MEDIUM confidence)
- [Real Python: Click and Python CLI Apps](https://realpython.com/python-click/)
- [CLI Interface Guidelines](https://clig.dev/)

---
*Architecture research for: Atlas Agent Management Platform*
*Researched: 2026-01-23*
