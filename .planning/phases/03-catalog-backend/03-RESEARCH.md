# Phase 3: Catalog Backend - Research

**Researched:** 2025-01-24
**Domain:** REST API design, PostgreSQL search, FastAPI patterns
**Confidence:** HIGH

## Summary

Phase 3 implements backend APIs to serve the catalog of skills, MCPs, and tools with search and filtering capabilities. The existing codebase already has a solid foundation from Phase 1: domain entities, repository interfaces, PostgreSQL repository implementation with basic ILIKE search, and content repository for GitHub integration.

The main work involves creating FastAPI route handlers that expose the repository functionality as REST endpoints, adding proper pagination, and optionally enhancing search with pg_trgm trigram indexes for better performance. Documentation retrieval (CATL-06) requires fetching README content from git via the existing ContentRepository.

**Primary recommendation:** Build a thin service layer for catalog operations, expose via standard RESTful routes with offset/limit pagination, use the existing ILIKE search (sufficient for MVP), and fetch documentation lazily from git on detail requests.

## Standard Stack

The established libraries/tools for this domain:

### Core (Already in Project)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.115+ | Web framework | Already used in project, async-native, automatic OpenAPI |
| SQLModel | 0.0.22 | ORM | Already used, combines SQLAlchemy + Pydantic |
| Pydantic | v2 | Schema validation | Bundled with FastAPI/SQLModel |
| asyncpg | 0.30+ | PostgreSQL driver | Already used, async-native |

### Supporting (Already Available)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PyGithub | 2.5+ | GitHub API | Already used for content repository |
| slowapi | 0.1.9+ | Rate limiting | Already configured in app |

### Not Needed
| Library | Reason Not to Use |
|---------|-------------------|
| fastapi-pagination | Adds complexity; manual pagination is simple enough for this use case and matches existing codebase patterns |
| elasticsearch | Overkill for catalog size; pg_trgm sufficient |
| redis | Premature optimization; can add caching later if needed |

**Installation:** No new dependencies required. All libraries already in `pyproject.toml`.

## Architecture Patterns

### Recommended Project Structure

Following existing patterns in the codebase:

```
backend/src/atlas/
├── domain/
│   ├── entities/catalog_item.py     # Already exists
│   └── interfaces/catalog_repository.py  # Already exists
├── application/
│   └── services/
│       └── catalog_service.py       # NEW: Business logic layer
├── adapters/
│   ├── postgresql/repositories/
│   │   └── catalog_repository.py    # Already exists (may need pagination)
│   └── github/
│       └── content_repository.py    # Already exists
└── entrypoints/
    └── api/
        └── routes/
            ├── __init__.py          # Update to export catalog_router
            └── catalog.py           # NEW: Catalog endpoints
```

### Pattern 1: Service Layer Between Routes and Repository

**What:** Thin service class that orchestrates repository calls and applies business logic
**When to use:** When routes need to combine data from multiple sources (catalog metadata + git content)

```python
# Source: Existing project patterns + industry best practice
class CatalogService:
    """Service layer for catalog operations."""

    def __init__(
        self,
        catalog_repo: AbstractCatalogRepository,
        content_repo: AbstractContentRepository,
    ) -> None:
        self._catalog_repo = catalog_repo
        self._content_repo = content_repo

    async def get_item_with_documentation(self, item_id: UUID) -> CatalogItemDetail:
        """Get catalog item with full documentation from git."""
        item = await self._catalog_repo.get_by_id(item_id)
        if item is None:
            raise CatalogItemNotFoundError(item_id)

        # Fetch documentation from git
        readme_path = self._get_readme_path(item.git_path)
        documentation = await self._content_repo.get_content(readme_path)

        return CatalogItemDetail(
            **item.model_dump(),
            documentation=documentation or "",
        )
```

### Pattern 2: Paginated List Response

**What:** Standard envelope for paginated results with metadata
**When to use:** All list endpoints

```python
# Source: FastAPI pagination best practices
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    """Standard pagination envelope."""
    items: list[T]
    total: int
    page: int
    size: int
    pages: int  # total_pages = ceil(total / size)
```

### Pattern 3: Query Parameters for Search/Filter

**What:** Use FastAPI Query parameters with validation
**When to use:** Search and filter endpoints

```python
# Source: Existing auth.py patterns in project
from fastapi import Query

@router.get("/catalog", response_model=PaginatedResponse[CatalogItemSummary])
async def list_catalog(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    type: Optional[CatalogItemType] = Query(default=None, description="Filter by type"),
    q: Optional[str] = Query(default=None, min_length=1, description="Search keyword"),
    catalog_service: CatalogService = Depends(get_catalog_service),
) -> PaginatedResponse[CatalogItemSummary]:
    ...
```

### Anti-Patterns to Avoid

- **Fat routes:** Don't put business logic in route handlers; use service layer
- **N+1 queries:** Don't fetch documentation for every item in list view; only on detail
- **Unbounded queries:** Always limit result size; enforce max page size
- **Mixing concerns:** Keep route handlers thin - validate, delegate, respond

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Search implementation | Custom search algorithm | PostgreSQL ILIKE (already implemented) | Existing repository.search() works; pg_trgm can be added later for optimization |
| Pagination math | Manual offset calculation | Simple formula: offset = (page - 1) * size | Standard pattern, no library needed |
| Response validation | Manual dict building | Pydantic response_model | FastAPI auto-validates and documents |
| Query param validation | Manual validation | FastAPI Query() with constraints | Built-in, generates OpenAPI |
| GitHub content caching | Custom cache layer | Start without cache; add redis later if needed | Premature optimization; GitHub API rate limit (5000/hr) is generous |

**Key insight:** The existing repository already has ILIKE-based search. For a catalog of hundreds/thousands of items (not millions), this is performant enough. Don't optimize prematurely.

## Common Pitfalls

### Pitfall 1: Fetching Documentation in List Endpoint

**What goes wrong:** Calling GitHub API for each item in list, causing N+1 requests and hitting rate limits
**Why it happens:** Developers try to return full documentation in list view
**How to avoid:** List endpoint returns summary only (no documentation). Detail endpoint fetches documentation.
**Warning signs:** List endpoint taking > 1 second, GitHub rate limit errors

### Pitfall 2: Missing Pagination on List Endpoints

**What goes wrong:** Returning all items when catalog grows large, causing memory issues
**Why it happens:** MVP starts small; pagination seems unnecessary
**How to avoid:** Implement pagination from day 1 with max size limit (e.g., 100)
**Warning signs:** Endpoint returning > 100 items, increasing memory usage

### Pitfall 3: Count Query Performance

**What goes wrong:** `SELECT COUNT(*)` becomes slow on large tables
**Why it happens:** PostgreSQL must scan all rows for accurate count
**How to avoid:** For MVP, accept the count query. If it becomes slow (> 100ms), consider:
  - Approximate count using `pg_stat_user_tables.reltuples`
  - Cache total count with short TTL
  - Return `has_more: bool` instead of total count
**Warning signs:** List endpoint > 500ms, count query appearing in slow query log

### Pitfall 4: GitHub API Failures Breaking Catalog

**What goes wrong:** GitHub API is down or rate-limited, entire detail endpoint fails
**Why it happens:** No error handling for external API
**How to avoid:** Return item metadata even if documentation fetch fails; include error flag
**Warning signs:** 500 errors when GitHub is slow, user can't browse catalog

### Pitfall 5: Case-Sensitive Search

**What goes wrong:** Search for "docker" doesn't find "Docker" items
**Why it happens:** Using LIKE instead of ILIKE
**How to avoid:** Already implemented correctly in repository using ILIKE
**Warning signs:** Users report "can't find" items that exist

## Code Examples

Verified patterns from official sources and existing project code:

### Route Handler with Pagination

```python
# Source: Existing project patterns (auth.py) + FastAPI docs
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from atlas.domain.entities.catalog_item import CatalogItemType
from atlas.entrypoints.dependencies import CatalogRepo, ContentRepo

router = APIRouter(prefix="/catalog", tags=["catalog"])


class CatalogItemSummary(BaseModel):
    """Summary view for catalog list (no documentation)."""
    id: UUID
    type: CatalogItemType
    name: str
    description: str
    tags: list[str]
    author_id: UUID
    team_id: Optional[UUID]
    usage_count: int


class CatalogItemDetail(BaseModel):
    """Detail view with full documentation."""
    id: UUID
    type: CatalogItemType
    name: str
    description: str
    git_path: str
    tags: list[str]
    author_id: UUID
    team_id: Optional[UUID]
    usage_count: int
    documentation: str  # README content from git


class PaginatedCatalog(BaseModel):
    """Paginated catalog response."""
    items: list[CatalogItemSummary]
    total: int
    page: int
    size: int
    pages: int


@router.get("", response_model=PaginatedCatalog)
async def list_catalog(
    catalog_repo: CatalogRepo,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    type: Optional[CatalogItemType] = Query(default=None, alias="type"),
    q: Optional[str] = Query(default=None, min_length=1),
) -> PaginatedCatalog:
    """
    List catalog items with optional filtering and search.

    - **page**: Page number (1-indexed)
    - **size**: Items per page (max 100)
    - **type**: Filter by item type (skill, mcp, tool)
    - **q**: Search keyword (searches name, description, tags)
    """
    # This requires adding pagination to repository - see below
    ...
```

### Repository Pagination Extension

```python
# Source: SQLAlchemy docs + existing repository patterns
# Add to AbstractCatalogRepository interface

from dataclasses import dataclass

@dataclass
class PaginatedResult:
    """Container for paginated query results."""
    items: list[CatalogItem]
    total: int

# Add method to interface:
@abstractmethod
async def list_paginated(
    self,
    offset: int,
    limit: int,
    item_type: Optional[CatalogItemType] = None,
    search_query: Optional[str] = None,
) -> PaginatedResult:
    """Retrieve paginated catalog items with optional filtering."""
    raise NotImplementedError


# PostgreSQL implementation:
async def list_paginated(
    self,
    offset: int,
    limit: int,
    item_type: Optional[CatalogItemType] = None,
    search_query: Optional[str] = None,
) -> PaginatedResult:
    """Retrieve paginated catalog items with optional filtering."""
    # Base query
    statement = select(CatalogItemModel)
    count_statement = select(func.count()).select_from(CatalogItemModel)

    # Apply type filter
    if item_type is not None:
        statement = statement.where(CatalogItemModel.type == item_type)
        count_statement = count_statement.where(CatalogItemModel.type == item_type)

    # Apply search filter
    if search_query:
        search_pattern = f"%{search_query}%"
        search_condition = or_(
            CatalogItemModel.name.ilike(search_pattern),
            CatalogItemModel.description.ilike(search_pattern),
            CatalogItemModel.tags.ilike(search_pattern),
        )
        statement = statement.where(search_condition)
        count_statement = count_statement.where(search_condition)

    # Get total count
    count_result = await self._session.execute(count_statement)
    total = count_result.scalar_one()

    # Apply pagination and ordering
    statement = statement.order_by(CatalogItemModel.name).offset(offset).limit(limit)

    result = await self._session.execute(statement)
    models = result.scalars().all()
    items = [catalog_item_model_to_entity(m) for m in models]

    return PaginatedResult(items=items, total=total)
```

### Detail Endpoint with Documentation

```python
# Source: Existing content_repository.py + project patterns

@router.get("/{item_id}", response_model=CatalogItemDetail)
async def get_catalog_item(
    item_id: UUID,
    catalog_repo: CatalogRepo,
    content_repo: ContentRepo,
) -> CatalogItemDetail:
    """
    Get catalog item details including full documentation.

    Documentation is fetched from the git repository.
    """
    # Get metadata from database
    item = await catalog_repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalog item not found",
        )

    # Attempt to fetch documentation from git
    # Convention: README.md in same directory as the item
    readme_path = _get_readme_path(item.git_path)
    documentation = ""
    try:
        documentation = await content_repo.get_content(readme_path) or ""
    except Exception:
        # Log error but don't fail - documentation is optional
        pass

    return CatalogItemDetail(
        id=item.id,
        type=item.type,
        name=item.name,
        description=item.description,
        git_path=item.git_path,
        tags=item.tags,
        author_id=item.author_id,
        team_id=item.team_id,
        usage_count=item.usage_count,
        documentation=documentation,
    )


def _get_readme_path(git_path: str) -> str:
    """
    Derive README path from item's git path.

    Convention: If item is at skills/my-skill/skill.yaml,
    look for skills/my-skill/README.md
    """
    # Get directory containing the item
    if "/" in git_path:
        directory = git_path.rsplit("/", 1)[0]
        return f"{directory}/README.md"
    return "README.md"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Custom validation | Pydantic v2 | 2023 | Faster, better errors |
| Sync SQLAlchemy | AsyncSession (SQLAlchemy 2.0+) | 2023 | Already using in project |
| LIKE search | ILIKE or pg_trgm | N/A | ILIKE already implemented |
| Manual OpenAPI | FastAPI auto-generation | N/A | Already using |

**Deprecated/outdated:**
- `response_model_include`/`response_model_exclude`: Use explicit response models instead
- Sync database access: Project already uses async; stay consistent
- GenericModel (Pydantic v1): Use Generic[T] with BaseModel in v2

## Open Questions

Things that couldn't be fully resolved:

1. **Documentation file convention**
   - What we know: Content is stored in git at paths like `skills/my-skill/...`
   - What's unclear: Exact file structure - is doc in README.md, skill.yaml frontmatter, or separate file?
   - Recommendation: Start with README.md convention; adjust if different pattern emerges from actual data

2. **Caching strategy for GitHub content**
   - What we know: GitHub API has 5000 req/hr limit; ETags support conditional requests
   - What's unclear: Expected traffic patterns, cache invalidation needs
   - Recommendation: Start without cache; add Redis later if needed (monitor GitHub API usage)

3. **Search relevance ranking**
   - What we know: Current ILIKE search returns unranked results
   - What's unclear: User expectations for search quality
   - Recommendation: Start with simple ILIKE; if users complain about relevance, add pg_trgm similarity scoring

## Sources

### Primary (HIGH confidence)
- Existing codebase files: `catalog_repository.py`, `content_repository.py`, `auth.py` routes
- [PostgreSQL pg_trgm documentation](https://www.postgresql.org/docs/current/pgtrgm.html) - trigram index capabilities
- [FastAPI Response Model documentation](https://fastapi.tiangolo.com/tutorial/response-model/) - response patterns

### Secondary (MEDIUM confidence)
- [FastAPI Pagination Best Practices](https://lewoudar.medium.com/fastapi-and-pagination-d27ad52983a) - pagination patterns
- [PostgreSQL GIN Index Guide](https://pganalyze.com/blog/gin-index) - index performance
- [GitHub API Rate Limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) - rate limiting details
- [FastAPI Service Layer Patterns](https://medium.com/@kacperwlodarczyk/fast-api-repository-pattern-and-service-layer-dad43354f07a) - architecture

### Tertiary (LOW confidence)
- Various Medium articles on pagination strategies (cross-verified with official docs)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using existing project dependencies
- Architecture: HIGH - Following established project patterns
- Search implementation: HIGH - ILIKE already implemented; pg_trgm is documented PostgreSQL feature
- Pagination: HIGH - Standard pattern with SQLAlchemy
- Documentation retrieval: MEDIUM - Git path conventions need validation against actual data
- Caching: LOW - Deferred; needs traffic analysis

**Research date:** 2025-01-24
**Valid until:** 2025-02-24 (30 days - stable domain, no major changes expected)
