# Phase 5: User Profiles Backend - Research

**Researched:** 2026-01-24
**Domain:** User dashboard aggregation, configuration inheritance computation, REST API design
**Confidence:** HIGH

## Summary

Phase 5 implements backend APIs to serve user dashboard data with configuration inheritance. This builds directly on Phases 2 (Auth), 3 (Catalog), and 4 (Configuration). The existing codebase provides all necessary infrastructure: User entity with team_ids, Team entity with member_ids, CatalogItem with team_id ownership, UserConfiguration with user-specific claude.md content, and established service/repository patterns.

The key work involves:
1. **Dashboard aggregation service**: Orchestrate User, Team, CatalogItem, and UserConfiguration data into a unified dashboard response
2. **Effective configuration computation**: Implement inheritance chain (org -> team -> user) using hierarchical merge pattern
3. **User profile REST endpoints**: Expose aggregated data through clean API endpoints

The architecture follows the established clean architecture pattern: services orchestrate multiple repositories, routes remain thin. Configuration inheritance is computed at runtime by merging configurations from org level (global defaults) to team level (team-specific additions) to user level (personal overrides).

**Primary recommendation:** Create a `UserProfileService` that aggregates data from existing repositories (UserRepository, TeamRepository, CatalogRepository, ConfigurationRepository, ContentRepository). Implement inheritance using a simple merge function that applies org defaults, then team configurations, then user-specific configurations. Use the existing Pydantic patterns for response models.

## Standard Stack

The established libraries/tools for this domain:

### Core (Already in Project)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.115+ | Web framework | Already used for all routes |
| Pydantic | v2 | Response models | Already used for all DTOs |
| SQLModel | 0.0.22 | ORM | Already used for database models |

### Supporting (Already Available)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| asyncio | stdlib | Async operations | Parallel repository calls |
| dataclasses | stdlib | Value objects | Inheritance chain results |

### Not Needed
| Library | Reason Not to Use |
|---------|-------------------|
| OmegaConf/Hydra | Overkill for simple 3-level hierarchy; custom merge is simpler |
| deepmerge | Simple dict merge is sufficient for configuration |
| graph databases | Relational model with join queries is adequate for org/team/user |

**Installation:** No new dependencies required. All libraries already in `pyproject.toml`.

## Architecture Patterns

### Recommended Project Structure

Following existing patterns in the codebase:

```
backend/src/atlas/
+-- domain/
|   +-- entities/
|   |   +-- effective_configuration.py    # NEW: EffectiveConfiguration value object
|   +-- interfaces/
|       # No new interfaces needed - reuse existing repositories
+-- application/
|   +-- services/
|   |   +-- user_profile_service.py       # NEW: Dashboard aggregation + inheritance
+-- adapters/
|   # No new adapters needed - reuse existing implementations
+-- entrypoints/
    +-- api/
        +-- routes/
            +-- profile.py                # NEW: User profile endpoints
```

### Pattern 1: Aggregation Service

**What:** A service that orchestrates multiple repositories to build a unified response
**When to use:** Dashboard endpoints that need data from multiple sources
**Why:** Keeps routes thin, enables caching, allows testing with mocked repositories

```python
# Source: Existing ConfigurationService pattern

class UserProfileService:
    """
    Aggregates user profile data from multiple sources.

    Combines user info, team memberships, available catalog items,
    and configuration with inheritance chain computed.
    """

    def __init__(
        self,
        user_repo: AbstractUserRepository,
        team_repo: AbstractTeamRepository,
        catalog_repo: AbstractCatalogRepository,
        config_repo: AbstractConfigurationRepository,
        content_repo: AbstractContentRepository,
    ) -> None:
        self._user_repo = user_repo
        self._team_repo = team_repo
        self._catalog_repo = catalog_repo
        self._config_repo = config_repo
        self._content_repo = content_repo

    async def get_dashboard(self, user_id: UUID) -> UserDashboard:
        """
        Get user's complete dashboard data.

        Includes: user info, teams, available items, configuration.
        """
        # Parallel fetch for performance
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)

        teams = await self._team_repo.get_user_teams(user_id)
        # ... aggregate remaining data
```

### Pattern 2: Hierarchical Configuration Merge

**What:** Merge configurations from multiple levels (org -> team -> user) with later levels overriding earlier
**When to use:** Effective configuration computation (PROF-03)
**Why:** Standard pattern for cascading defaults; simple to implement and test

```python
# Source: Project architecture decisions, cascade-config pattern

from dataclasses import dataclass
from typing import Optional

@dataclass
class EffectiveConfiguration:
    """
    Represents the computed effective configuration for a user.

    Shows what comes from each level in the inheritance chain.
    """
    content: str                     # Final merged configuration
    org_contribution: str            # What came from org level
    team_contribution: str           # What came from team level
    user_contribution: str           # What came from user level
    source_breakdown: dict[str, str] # Which level provided which section

def merge_configurations(
    org_config: Optional[str],
    team_configs: list[str],
    user_config: Optional[str],
) -> EffectiveConfiguration:
    """
    Merge configurations with cascade override pattern.

    Order: org defaults -> team additions -> user overrides

    For claude.md (markdown content), merging means:
    - Concatenate content from each level with clear section markers
    - User-level content takes precedence for any conflicting sections
    - Empty levels contribute nothing
    """
    sections = []

    if org_config:
        sections.append(("organization", org_config))

    for team_config in team_configs:
        if team_config:
            sections.append(("team", team_config))

    if user_config:
        sections.append(("user", user_config))

    # Combine all sections
    merged_content = "\n\n".join(
        f"# [{source.upper()}]\n{content}"
        for source, content in sections
    )

    return EffectiveConfiguration(
        content=merged_content,
        org_contribution=org_config or "",
        team_contribution="\n".join(team_configs) if team_configs else "",
        user_contribution=user_config or "",
        source_breakdown={
            "organization": "global defaults",
            "team": f"{len(team_configs)} team config(s)",
            "user": "personal overrides" if user_config else "none",
        },
    )
```

### Pattern 3: Available Items Computation

**What:** Compute user's effective available skills/MCPs/tools based on team membership
**When to use:** PROF-02 - showing what items a user can access
**Why:** Users see items from: company-wide (no team_id) + their team(s)

```python
# Source: Existing catalog_repo.list_by_team pattern

async def get_available_items(
    self,
    user_id: UUID,
) -> list[CatalogItem]:
    """
    Get all catalog items available to a user.

    Available = company-wide items (team_id=None) + items from user's teams
    """
    # Get user's teams
    user = await self._user_repo.get_by_id(user_id)
    if user is None:
        return []

    # Fetch company-wide items (no team restriction)
    all_items = await self._catalog_repo.list_all()

    # Filter to: items without team OR items from user's teams
    available = [
        item for item in all_items
        if item.team_id is None or item.team_id in user.team_ids
    ]

    return available
```

### Anti-Patterns to Avoid

- **N+1 queries for teams:** Fetch all user's teams in one query, not per-item lookups
- **Recomputing inheritance on every request:** If performance matters, cache effective config with TTL
- **Storing computed configuration:** Effective config is computed at runtime; only source configs are stored
- **Circular team inheritance:** Keep hierarchy simple: org -> team -> user (no team-to-team)
- **Blocking aggregation calls:** Use asyncio.gather for parallel repository calls when possible

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| User's teams lookup | Manual join | `team_repo.get_user_teams(user_id)` | Already exists, tested |
| Team's items lookup | Filter in memory | `catalog_repo.list_by_team(team_id)` | Already exists with indexing |
| User config retrieval | Direct DB query | `config_service.get_configuration()` | Handles git content + DB metadata |
| Parallel async calls | Sequential awaits | `asyncio.gather()` | Built-in, faster |

**Key insight:** This phase is primarily orchestration of existing capabilities. The repositories and services from Phases 1-4 provide all the data access patterns needed. The new work is aggregation and inheritance computation, not new data operations.

## Common Pitfalls

### Pitfall 1: Missing User Validation

**What goes wrong:** Profile endpoints called for non-existent user IDs
**Why it happens:** CurrentUser dependency validates token, but user could be deleted between auth and request
**How to avoid:**
- Always check `user_repo.get_by_id()` result for None
- Raise 404 immediately if user not found
- Don't assume CurrentUser.id is always valid for data queries
**Warning signs:** Null pointer errors in service layer

### Pitfall 2: Configuration Inheritance Complexity Creep

**What goes wrong:** Inheritance logic becomes complex with edge cases
**Why it happens:** Trying to support too many inheritance scenarios
**How to avoid:**
- Keep to simple 3-level hierarchy: org -> team -> user
- No team-to-team inheritance (defer to Phase 9 if needed)
- User config always wins for conflicts
- Empty levels contribute nothing (not special "null" values)
**Warning signs:** Complex merge logic, many special cases

### Pitfall 3: Team Configuration Storage

**What goes wrong:** Where to store team-level configuration isn't clear
**Why it happens:** UserConfiguration is per-user; no TeamConfiguration exists yet
**How to avoid:**
- For v1, org-level config is a single well-known path: `configs/organization/claude.md`
- For v1, team-level configs are at: `configs/teams/{team_id}/claude.md`
- These are fetched via ContentRepository (same pattern as user config)
- Database metadata is optional for team configs in v1 (can be added later)
**Warning signs:** Creating new database tables when git content suffices

### Pitfall 4: N+1 Query Problem in Dashboard

**What goes wrong:** Dashboard endpoint makes many sequential database calls
**Why it happens:** Fetching teams, then items per team, then configs per team
**How to avoid:**
- Use asyncio.gather() for parallel fetches
- Fetch all user's teams in single query
- Fetch all catalog items once, filter in Python
- Keep dashboard to essential data only
**Warning signs:** Slow dashboard endpoint, many DB roundtrips

### Pitfall 5: Missing Configuration Levels

**What goes wrong:** API returns empty config when org/team configs don't exist
**Why it happens:** get_content returns None for non-existent files
**How to avoid:**
- Treat missing config as empty string ""
- Always return EffectiveConfiguration, even if all levels empty
- Frontend decides what to show for empty configs
**Warning signs:** Null responses, frontend errors

### Pitfall 6: Overly Complex Response Models

**What goes wrong:** Dashboard response includes too much nested data
**Why it happens:** Trying to return everything in one call
**How to avoid:**
- Dashboard returns summary data only
- Detail endpoints for full item/config info
- Reference IDs for lists, not full objects
- Consider separate endpoints vs. one mega-response
**Warning signs:** Large response payloads, slow serialization

## Code Examples

Verified patterns from existing project code:

### UserDashboard Response Model

```python
# Source: Existing pattern from catalog.py, configuration.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from atlas.domain.entities.catalog_item import CatalogItemType


class TeamSummary(BaseModel):
    """Summary of a team for dashboard display."""
    id: UUID
    name: str
    member_count: int


class CatalogItemSummary(BaseModel):
    """Summary of available catalog item."""
    id: UUID
    type: CatalogItemType
    name: str
    description: str


class EffectiveConfigurationResponse(BaseModel):
    """Effective configuration with inheritance breakdown."""
    content: str                    # Final merged config
    org_applied: bool               # Whether org config contributed
    team_applied: bool              # Whether team config(s) contributed
    user_applied: bool              # Whether user config contributed
    last_updated: Optional[datetime]


class UserDashboard(BaseModel):
    """Complete dashboard data for authenticated user."""

    # User info
    user_id: UUID
    username: str
    email: str

    # Team memberships
    teams: list[TeamSummary]

    # Available items summary (counts by type)
    available_skills: int
    available_mcps: int
    available_tools: int

    # Configuration status
    has_configuration: bool
    configuration_updated_at: Optional[datetime]
```

### UserProfileService Implementation

```python
# Source: Existing ConfigurationService pattern

from uuid import UUID
import asyncio

from atlas.domain.entities import User
from atlas.domain.interfaces import (
    AbstractUserRepository,
    AbstractTeamRepository,
    AbstractCatalogRepository,
    AbstractConfigurationRepository,
    AbstractContentRepository,
)


class UserNotFoundError(Exception):
    """Raised when user doesn't exist."""
    pass


class UserProfileService:
    """
    Aggregates user profile data from multiple sources.
    """

    def __init__(
        self,
        user_repo: AbstractUserRepository,
        team_repo: AbstractTeamRepository,
        catalog_repo: AbstractCatalogRepository,
        config_repo: AbstractConfigurationRepository,
        content_repo: AbstractContentRepository,
    ) -> None:
        self._user_repo = user_repo
        self._team_repo = team_repo
        self._catalog_repo = catalog_repo
        self._config_repo = config_repo
        self._content_repo = content_repo

    async def get_dashboard(self, user_id: UUID) -> UserDashboard:
        """Get user's complete dashboard data."""
        # Fetch user first (required)
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")

        # Parallel fetch for remaining data
        teams_task = self._team_repo.get_user_teams(user_id)
        items_task = self._catalog_repo.list_all()
        config_task = self._config_repo.get_by_user_id(user_id)

        teams, all_items, config = await asyncio.gather(
            teams_task, items_task, config_task
        )

        # Filter items available to user
        available = [
            item for item in all_items
            if item.team_id is None or item.team_id in user.team_ids
        ]

        # Count by type
        skills = sum(1 for i in available if i.type.value == "skill")
        mcps = sum(1 for i in available if i.type.value == "mcp")
        tools = sum(1 for i in available if i.type.value == "tool")

        return UserDashboard(
            user_id=user.id,
            username=user.username,
            email=user.email,
            teams=[
                TeamSummary(id=t.id, name=t.name, member_count=t.member_count)
                for t in teams
            ],
            available_skills=skills,
            available_mcps=mcps,
            available_tools=tools,
            has_configuration=config is not None,
            configuration_updated_at=config.updated_at if config else None,
        )
```

### Effective Configuration Computation

```python
# Source: cascade-config pattern adapted for project

from dataclasses import dataclass
from typing import Optional


@dataclass
class EffectiveConfiguration:
    """Computed effective configuration with source breakdown."""
    content: str
    org_content: str
    team_content: str
    user_content: str


class EffectiveConfigurationService:
    """Computes effective configuration from inheritance chain."""

    # Well-known paths for org/team configs
    ORG_CONFIG_PATH = "configs/organization/claude.md"

    def __init__(
        self,
        content_repo: AbstractContentRepository,
        config_repo: AbstractConfigurationRepository,
        team_repo: AbstractTeamRepository,
    ) -> None:
        self._content_repo = content_repo
        self._config_repo = config_repo
        self._team_repo = team_repo

    def _team_config_path(self, team_id: UUID) -> str:
        """Generate path for team configuration."""
        return f"configs/teams/{team_id}/claude.md"

    async def get_effective_configuration(
        self,
        user_id: UUID,
    ) -> EffectiveConfiguration:
        """
        Compute effective configuration for user.

        Merges: org config -> team config(s) -> user config
        """
        # Fetch user's teams
        teams = await self._team_repo.get_user_teams(user_id)

        # Fetch all configs in parallel
        org_task = self._content_repo.get_content(self.ORG_CONFIG_PATH)
        team_tasks = [
            self._content_repo.get_content(self._team_config_path(t.id))
            for t in teams
        ]
        user_config = await self._config_repo.get_by_user_id(user_id)
        user_task = (
            self._content_repo.get_content(user_config.git_path)
            if user_config else None
        )

        # Await all
        org_content = await org_task
        team_contents = await asyncio.gather(*team_tasks)
        user_content = await user_task if user_task else None

        # Merge with clear markers
        sections = []

        if org_content:
            sections.append(f"# Organization Configuration\n\n{org_content}")

        for i, (team, content) in enumerate(zip(teams, team_contents)):
            if content:
                sections.append(f"# Team: {team.name}\n\n{content}")

        if user_content:
            sections.append(f"# Personal Configuration\n\n{user_content}")

        merged = "\n\n---\n\n".join(sections) if sections else ""

        return EffectiveConfiguration(
            content=merged,
            org_content=org_content or "",
            team_content="\n\n".join(c for c in team_contents if c) or "",
            user_content=user_content or "",
        )
```

### Profile Routes

```python
# Source: Existing catalog.py and configuration.py patterns

from fastapi import APIRouter, HTTPException, status

from atlas.entrypoints.dependencies import CurrentUser

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/dashboard")
async def get_dashboard(
    current_user: CurrentUser,
    profile_service: ProfileService,  # Type alias like ConfigService
) -> UserDashboard:
    """
    Get current user's dashboard data.

    Returns aggregated view of user's teams, available items, and config status.
    """
    try:
        return await profile_service.get_dashboard(current_user.id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.get("/available-items")
async def get_available_items(
    current_user: CurrentUser,
    profile_service: ProfileService,
    type: Optional[CatalogItemType] = None,
) -> list[CatalogItemSummary]:
    """
    Get catalog items available to current user.

    Returns company-wide items plus items from user's teams.
    Optionally filter by type (skill, mcp, tool).
    """
    items = await profile_service.get_available_items(current_user.id)
    if type:
        items = [i for i in items if i.type == type]
    return items


@router.get("/effective-configuration")
async def get_effective_configuration(
    current_user: CurrentUser,
    effective_config_service: EffectiveConfigService,
) -> EffectiveConfigurationResponse:
    """
    Get user's effective configuration with inheritance chain.

    Shows merged configuration from org -> team -> user levels.
    """
    config = await effective_config_service.get_effective_configuration(
        current_user.id
    )
    return EffectiveConfigurationResponse(
        content=config.content,
        org_applied=bool(config.org_content),
        team_applied=bool(config.team_content),
        user_applied=bool(config.user_content),
        last_updated=None,  # Could track from user config
    )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Separate endpoints per data type | Aggregation service pattern | Best practice | Fewer round trips, better DX |
| Sequential async calls | asyncio.gather() for parallel | Python 3.4+ | Faster dashboard loads |
| Complex inheritance rules | Simple 3-level cascade | Keep simple | Easier to understand and debug |
| Store computed config | Compute on demand | Best practice | Single source of truth in git |

**Deprecated/outdated:**
- Storing effective configuration in database (recomputes on access instead)
- Per-item permissions queries (use team membership filtering)

## Open Questions

Things that couldn't be fully resolved:

1. **Organization Configuration Ownership**
   - What we know: Org config stored at `configs/organization/claude.md`
   - What's unclear: Who can edit org config? (Admin only vs. any user)
   - Recommendation: For v1, treat as read-only at API level; edits via git/admin

2. **Team Configuration Creation**
   - What we know: Team configs at `configs/teams/{team_id}/claude.md`
   - What's unclear: Should there be CRUD endpoints for team configs?
   - Recommendation: Defer to Phase 9 (Governance); v1 focuses on user profile reading

3. **Configuration Merge Semantics**
   - What we know: Simple concatenation with section markers
   - What's unclear: Should identical sections dedupe? Should user override team?
   - Recommendation: For v1, concatenate all with markers; frontend can interpret

4. **Caching Strategy**
   - What we know: Dashboard aggregates from multiple sources
   - What's unclear: Expected request frequency, acceptable staleness
   - Recommendation: No caching for v1; add if performance requires

## Sources

### Primary (HIGH confidence)
- Existing codebase: `configuration_service.py`, `catalog.py`, `dependencies.py` - established patterns
- Project STATE.md - prior decisions on architecture
- Phase 4 RESEARCH.md - configuration patterns already researched

### Secondary (MEDIUM confidence)
- [cascade-config](https://cascade-config.readthedocs.io/en/latest/) - hierarchical configuration merge patterns
- [Adobe himl](https://github.com/adobe/himl) - hierarchical YAML merge patterns
- [FastAPI service layer patterns](https://medium.com/@abhinav.dobhal/building-production-ready-fastapi-applications-with-service-layer-architecture-in-2025-f3af8a6ac563) - aggregation service architecture

### Tertiary (LOW confidence)
- General WebSearch results on configuration inheritance (informed design decisions)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using only existing project dependencies
- Architecture: HIGH - Following established project patterns (service layer, repository pattern)
- Aggregation service: HIGH - Straightforward extension of ConfigurationService
- Inheritance computation: MEDIUM - Simple pattern but edge cases may emerge
- Response models: HIGH - Consistent with existing catalog/configuration endpoints

**Research date:** 2026-01-24
**Valid until:** 2026-02-24 (30 days - stable domain, no external dependencies)
