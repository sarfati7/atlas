# Phase 4: Configuration Backend - Research

**Researched:** 2026-01-24
**Domain:** Git-backed user configuration versioning, REST API design, FastAPI file uploads
**Confidence:** HIGH

## Summary

Phase 4 implements backend APIs for user configuration management (claude.md files) with git-backed versioning and rollback capabilities. The existing codebase provides a solid foundation: ContentRepository interface with GitHub/in-memory implementations already supports save_content, get_content, and get_commit_sha operations. User entity and authentication are complete from Phase 2. The key work involves:

1. Adding a UserConfiguration domain entity and corresponding database model to track user configurations
2. Extending ContentRepository interface with version history retrieval methods
3. Creating configuration service layer that orchestrates database metadata + git content
4. Building REST endpoints for CRUD, version history, rollback, and file import

The architecture follows the existing clean architecture pattern: Git stores ONLY content, PostgreSQL stores ALL metadata. Each configuration edit creates a new git commit, with the commit SHA stored in the database for version tracking.

**Primary recommendation:** Store configuration metadata (user_id, git_path, version, commit_sha, created_at) in PostgreSQL while storing actual claude.md content in git. Use PyGithub's `get_commits(path=...)` for version history and `get_contents(path, ref=commit_sha)` for rollback. Leverage existing ContentRepository patterns.

## Standard Stack

The established libraries/tools for this domain:

### Core (Already in Project)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.115+ | Web framework | Already used, async-native, file upload support |
| SQLModel | 0.0.22 | ORM | Already used for User, Team, CatalogItem models |
| PyGithub | 2.5+ | GitHub API | Already used in GitHubContentRepository |
| python-multipart | 0.0.18 | File uploads | Already in dependencies, required for UploadFile |
| asyncpg | 0.30+ | PostgreSQL driver | Already used for async DB operations |

### Supporting (Already Available)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pydantic | v2 | Schema validation | Request/response models |
| asyncio.to_thread | stdlib | Sync-to-async wrapper | Wrap PyGithub sync calls |

### Not Needed
| Library | Reason Not to Use |
|---------|-------------------|
| aiofiles | Not needed; we read content from git, not local filesystem |
| GitPython | PyGithub already handles GitHub API; no local git operations needed |
| Temporal databases | Overkill; simple version table with commit SHAs is sufficient |

**Installation:** No new dependencies required. All libraries already in `pyproject.toml`.

## Architecture Patterns

### Recommended Project Structure

Following existing patterns in the codebase:

```
backend/src/atlas/
+-- domain/
|   +-- entities/
|   |   +-- user_configuration.py     # NEW: Configuration entity with version info
|   +-- interfaces/
|   |   +-- configuration_repository.py  # NEW: Configuration metadata repository
|   |   +-- content_repository.py     # EXTEND: Add version history methods
+-- application/
|   +-- services/
|   |   +-- configuration_service.py  # NEW: Orchestrates DB + git operations
+-- adapters/
|   +-- postgresql/
|   |   +-- models.py                 # EXTEND: Add UserConfigurationModel
|   |   +-- repositories/
|   |       +-- configuration_repository.py  # NEW: PostgreSQL implementation
|   +-- github/
|   |   +-- content_repository.py     # EXTEND: Add get_version_history()
|   +-- in_memory/
|       +-- content_repository.py     # EXTEND: Add get_version_history()
|       +-- repositories/
|           +-- configuration_repository.py  # NEW: In-memory implementation
+-- entrypoints/
    +-- api/
        +-- routes/
            +-- configuration.py      # NEW: Configuration endpoints
```

### Pattern 1: Dual Storage - Git Content + DB Metadata

**What:** Store claude.md content in git, store metadata (user, version, timestamps, commit SHA) in PostgreSQL
**When to use:** All configuration operations - this is the project's core data architecture principle
**Why:** Git provides natural versioning, audit trail, and rollback. PostgreSQL enables fast queries, user association, and relational integrity.

```python
# Source: Project architecture decisions (CONTEXT.md)

# Database stores metadata
class UserConfigurationModel(SQLModel, table=True):
    __tablename__ = "user_configurations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    git_path: str = Field(unique=True)  # e.g., "configs/users/{user_id}/claude.md"
    current_commit_sha: str  # Points to latest git commit
    created_at: datetime
    updated_at: datetime

# Git stores actual content
# Path convention: configs/users/{user_id}/claude.md
```

### Pattern 2: Version History via Git Commits

**What:** Retrieve version history using PyGithub's get_commits() with path filter
**When to use:** Version history endpoint, rollback operations
**Why:** Git is the source of truth for versions; database only tracks current state

```python
# Source: PyGithub docs (https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html)

class GitHubContentRepository(AbstractContentRepository):

    async def get_version_history(
        self,
        path: str,
        limit: int = 50
    ) -> list[ConfigurationVersion]:
        """Get commit history for a file."""
        commits = await asyncio.to_thread(
            self._repo.get_commits,
            path=path
        )
        versions = []
        for i, commit in enumerate(commits):
            if i >= limit:
                break
            versions.append(ConfigurationVersion(
                commit_sha=commit.sha,
                message=commit.commit.message,
                author=commit.commit.author.name,
                timestamp=commit.commit.author.date,
            ))
        return versions

    async def get_content_at_version(
        self,
        path: str,
        commit_sha: str
    ) -> Optional[str]:
        """Get file content at specific commit SHA."""
        try:
            content = await asyncio.to_thread(
                self._repo.get_contents,
                path,
                ref=commit_sha
            )
            return content.decoded_content.decode("utf-8")
        except GithubException:
            return None
```

### Pattern 3: Service Layer for Configuration Operations

**What:** ConfigurationService orchestrates repository calls and enforces business rules
**When to use:** All configuration operations (CRUD, history, rollback, import)
**Why:** Clean separation of concerns; routes remain thin

```python
# Source: Existing project patterns (catalog.py, auth.py)

class ConfigurationService:
    def __init__(
        self,
        config_repo: AbstractConfigurationRepository,
        content_repo: AbstractContentRepository,
    ):
        self._config_repo = config_repo
        self._content_repo = content_repo

    async def save_configuration(
        self,
        user_id: UUID,
        content: str,
        message: Optional[str] = None,
    ) -> UserConfiguration:
        """Save configuration with git versioning."""
        path = self._get_user_config_path(user_id)
        commit_message = message or f"Update configuration for user {user_id}"

        # Save to git
        commit_sha = await self._content_repo.save_content(
            path=path,
            content=content,
            message=commit_message,
        )

        # Update database metadata
        config = await self._config_repo.get_by_user_id(user_id)
        if config is None:
            config = UserConfiguration(
                user_id=user_id,
                git_path=path,
                current_commit_sha=commit_sha,
            )
        else:
            config.current_commit_sha = commit_sha
            config.updated_at = datetime.utcnow()

        return await self._config_repo.save(config)

    def _get_user_config_path(self, user_id: UUID) -> str:
        return f"configs/users/{user_id}/claude.md"
```

### Pattern 4: File Import via UploadFile

**What:** Accept .md file uploads using FastAPI's UploadFile
**When to use:** Import existing claude.md from local machine (CONF-05)
**Why:** Standard FastAPI pattern for file uploads

```python
# Source: FastAPI docs (https://fastapi.tiangolo.com/tutorial/request-files/)

@router.post("/import", response_model=ConfigurationResponse)
async def import_configuration(
    file: UploadFile,
    current_user: CurrentUser,
    config_service: ConfigService,
) -> ConfigurationResponse:
    """Import an existing claude.md file."""
    # Validate file type
    if not file.filename or not file.filename.endswith(".md"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a .md file",
        )

    # Read content
    content = await file.read()
    try:
        content_str = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be valid UTF-8 text",
        )

    # Save via service
    config = await config_service.save_configuration(
        user_id=current_user.id,
        content=content_str,
        message="Import configuration from local file",
    )

    return ConfigurationResponse(...)
```

### Anti-Patterns to Avoid

- **Storing content in database:** Git is the source of truth for content - database only tracks metadata
- **Bypassing service layer:** All operations must go through ConfigurationService to ensure git + DB consistency
- **Hardcoded paths:** Use service methods to construct git paths consistently
- **Sync operations in route handlers:** Always use asyncio.to_thread for PyGithub calls
- **Unbounded history queries:** Always limit version history results (default 50)

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Version history | Custom version tracking table | PyGithub get_commits(path=...) | Git already tracks all versions; duplicating is error-prone |
| Rollback | Copy old content manually | get_contents(path, ref=sha) + save_content() | GitHub API provides content at any commit |
| File upload handling | Manual multipart parsing | FastAPI UploadFile | Built-in, handles encoding, temp files |
| Content diffing | Custom diff algorithm | Frontend handles it (or use difflib) | Content is text; standard diff works |
| Commit messages | Hardcoded strings | User-provided or sensible defaults | Better audit trail with meaningful messages |

**Key insight:** Git is already a version control system. The database only needs to track "which user owns which config path" and "what's the current commit SHA." History, diffs, and rollback are all git operations.

## Common Pitfalls

### Pitfall 1: Race Conditions on Concurrent Saves

**What goes wrong:** Two users save simultaneously; second save fails or overwrites first
**Why it happens:** PyGithub update_file requires current file SHA; concurrent saves have same SHA
**How to avoid:**
- For user configs (one user = one file), this is inherently safe since only the owner can edit
- If multi-editor needed, implement optimistic locking with version check in service layer
**Warning signs:** "Conflict" errors from GitHub API

### Pitfall 2: GitHub API Rate Limiting

**What goes wrong:** Version history queries fail with 403 after many requests
**Why it happens:** GitHub has 5000 requests/hour for authenticated users
**How to avoid:**
- Cache version history results (short TTL, 60 seconds)
- Limit history results (max 50 versions)
- Batch operations where possible
**Warning signs:** Intermittent 403 errors, especially during testing

### Pitfall 3: Large File Content in Memory

**What goes wrong:** Import of very large files causes memory issues
**Why it happens:** UploadFile.read() loads entire file into memory
**How to avoid:**
- Validate file size before processing (recommend 1MB limit for claude.md)
- Use chunked reading for larger files if ever needed
**Warning signs:** Memory spikes during import, OOM errors

### Pitfall 4: Missing User Configuration

**What goes wrong:** Get/update endpoints fail for users who haven't created config yet
**Why it happens:** No default configuration created on user registration
**How to avoid:**
- Handle "config not found" gracefully in service
- Return empty/default content for GET if no config exists
- Create config on first save (upsert pattern)
**Warning signs:** 404 errors for new users trying to view their config

### Pitfall 5: Git Path Collisions

**What goes wrong:** Two different entities point to same git path
**Why it happens:** Path generation logic has bugs or doesn't use unique identifiers
**How to avoid:**
- Use UUID in path: `configs/users/{user_id}/claude.md`
- Add unique constraint on git_path in database
- Validate path format in service layer
**Warning signs:** Database constraint violations, wrong content returned

### Pitfall 6: Missing asyncio.to_thread Wrapper

**What goes wrong:** PyGithub sync calls block the event loop
**Why it happens:** Developer forgets PyGithub is synchronous
**How to avoid:**
- All PyGithub calls MUST use asyncio.to_thread
- Enforce in code review
- Add type hints that make async clear
**Warning signs:** Slow endpoint responses, reduced concurrency

## Code Examples

Verified patterns from official sources and existing project code:

### Database Model for Configuration Metadata

```python
# Source: Existing models.py patterns + Phase 1 RESEARCH

class UserConfigurationModel(SQLModel, table=True):
    """SQLModel table for user configuration metadata."""

    __tablename__ = "user_configurations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True)
    git_path: str = Field(unique=True)  # e.g., "configs/users/{uuid}/claude.md"
    current_commit_sha: str = Field(default="")  # Empty until first save
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Extended Content Repository Interface

```python
# Source: Existing content_repository.py interface

from dataclasses import dataclass
from datetime import datetime

@dataclass
class ConfigurationVersion:
    """Represents a version (commit) of a configuration file."""
    commit_sha: str
    message: str
    author: str
    timestamp: datetime

class AbstractContentRepository(ABC):
    # ... existing methods ...

    @abstractmethod
    async def get_version_history(
        self,
        path: str,
        limit: int = 50
    ) -> list[ConfigurationVersion]:
        """
        Get commit history for a file.

        Returns list of versions ordered by timestamp (newest first).
        """
        raise NotImplementedError

    @abstractmethod
    async def get_content_at_version(
        self,
        path: str,
        commit_sha: str
    ) -> Optional[str]:
        """
        Get file content at a specific commit SHA.

        Returns None if file or commit doesn't exist.
        """
        raise NotImplementedError
```

### Configuration REST Endpoints

```python
# Source: Existing auth.py and catalog.py patterns

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel

router = APIRouter(prefix="/configuration", tags=["configuration"])


class ConfigurationResponse(BaseModel):
    """Response containing configuration content and metadata."""
    content: str
    commit_sha: str
    updated_at: datetime


class ConfigurationUpdateRequest(BaseModel):
    """Request to update configuration content."""
    content: str
    message: Optional[str] = None  # Commit message


class VersionResponse(BaseModel):
    """Single version in history."""
    commit_sha: str
    message: str
    author: str
    timestamp: datetime


class VersionHistoryResponse(BaseModel):
    """Version history response."""
    versions: list[VersionResponse]
    total: int


@router.get("/me", response_model=ConfigurationResponse)
async def get_my_configuration(
    current_user: CurrentUser,
    config_service: ConfigService,
) -> ConfigurationResponse:
    """Get current user's configuration."""
    ...


@router.put("/me", response_model=ConfigurationResponse)
async def update_my_configuration(
    body: ConfigurationUpdateRequest,
    current_user: CurrentUser,
    config_service: ConfigService,
) -> ConfigurationResponse:
    """Update current user's configuration."""
    ...


@router.get("/me/history", response_model=VersionHistoryResponse)
async def get_configuration_history(
    current_user: CurrentUser,
    config_service: ConfigService,
    limit: int = Query(default=50, ge=1, le=100),
) -> VersionHistoryResponse:
    """Get version history of user's configuration."""
    ...


@router.post("/me/rollback/{commit_sha}", response_model=ConfigurationResponse)
async def rollback_configuration(
    commit_sha: str,
    current_user: CurrentUser,
    config_service: ConfigService,
) -> ConfigurationResponse:
    """Rollback configuration to a previous version."""
    ...


@router.post("/me/import", response_model=ConfigurationResponse)
async def import_configuration(
    file: UploadFile,
    current_user: CurrentUser,
    config_service: ConfigService,
) -> ConfigurationResponse:
    """Import configuration from uploaded .md file."""
    ...
```

### Rollback Implementation

```python
# Source: PyGithub docs + project patterns

async def rollback_to_version(
    self,
    user_id: UUID,
    commit_sha: str,
) -> UserConfiguration:
    """Rollback configuration to a previous version."""
    config = await self._config_repo.get_by_user_id(user_id)
    if config is None:
        raise ConfigurationNotFoundError(user_id)

    # Get content from historical commit
    old_content = await self._content_repo.get_content_at_version(
        path=config.git_path,
        commit_sha=commit_sha,
    )
    if old_content is None:
        raise VersionNotFoundError(commit_sha)

    # Save as new commit (creates new version pointing to old content)
    new_sha = await self._content_repo.save_content(
        path=config.git_path,
        content=old_content,
        message=f"Rollback to version {commit_sha[:7]}",
    )

    # Update database metadata
    config.current_commit_sha = new_sha
    config.updated_at = datetime.utcnow()

    return await self._config_repo.save(config)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Store versions in separate DB table | Use git commit history | Best practice | Eliminates version table, git is already a VCS |
| Sync PyGithub calls | asyncio.to_thread wrapper | Python 3.9+ | Non-blocking API calls in async context |
| Form-encoded file uploads | UploadFile with multipart | FastAPI standard | Better file handling, automatic temp files |
| Manual SHA tracking | Let git handle versioning | Best practice | Simpler code, no version number management |

**Deprecated/outdated:**
- Storing full content in database alongside git (duplicates data, sync issues)
- Using GitPython for GitHub operations (PyGithub is more appropriate for API access)
- Custom version numbering (git SHAs are unique identifiers)

## Open Questions

Things that couldn't be fully resolved:

1. **Content size limit for claude.md files**
   - What we know: GitHub API limits: files up to 1MB return full content, 1-100MB need special handling
   - What's unclear: Expected typical size of claude.md files
   - Recommendation: Start with 1MB limit; sufficient for most configuration files

2. **Default content for new users**
   - What we know: Users without configuration will get 404 or empty response
   - What's unclear: Should we provide a template? What content?
   - Recommendation: Return empty string for GET if no config exists; let frontend handle default template

3. **Caching strategy for version history**
   - What we know: GitHub API has rate limits (5000/hr authenticated)
   - What's unclear: Expected frequency of history queries
   - Recommendation: Start without caching; add if rate limits become an issue (monitor usage)

4. **Commit message format**
   - What we know: Git commits need messages; user can optionally provide
   - What's unclear: Best default format, whether to include metadata
   - Recommendation: Use descriptive defaults like "Update configuration" or "Rollback to {sha[:7]}"

## Sources

### Primary (HIGH confidence)
- [PyGithub Repository Documentation](https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html) - get_commits(), get_contents() with ref parameter
- [GitHub REST API - Repository Contents](https://docs.github.com/en/rest/repos/contents) - ref parameter for historical content
- [FastAPI Request Files](https://fastapi.tiangolo.com/tutorial/request-files/) - UploadFile patterns
- Existing codebase: content_repository.py, auth.py routes, models.py patterns

### Secondary (MEDIUM confidence)
- [System-Versioned Tables in PostgreSQL](https://hypirion.com/musings/implementing-system-versioned-tables-in-postgres) - Alternative versioning patterns (not used, but informed design)
- [Evil Martians Soft Deletion](https://evilmartians.com/chronicles/soft-deletion-with-postgresql-but-with-logic-on-the-database) - Database patterns

### Tertiary (LOW confidence)
- Various WebSearch results on REST API versioning (general patterns, not specific implementations)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using existing project dependencies only
- Architecture: HIGH - Following established project patterns (git content, DB metadata)
- Version history: HIGH - PyGithub API is well-documented
- Rollback: HIGH - Simple pattern of get-at-version + save
- File upload: HIGH - Standard FastAPI pattern already in dependencies
- Database schema: MEDIUM - Simple extension of existing patterns, but needs validation

**Research date:** 2026-01-24
**Valid until:** 2026-02-24 (30 days - stable domain, mature libraries)
