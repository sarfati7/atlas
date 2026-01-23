# Phase 1: Foundation & Data Architecture - Research

**Researched:** 2025-01-23
**Domain:** Python FastAPI backend with PostgreSQL, SQLModel ORM, Git integration, Clean Architecture
**Confidence:** HIGH

## Summary

This phase establishes the foundational data layer with correct git/database separation. The research confirms that the decided stack (FastAPI + SQLModel + PostgreSQL + Alembic) is well-supported with mature patterns for async operations, migrations, and clean architecture. The key technical areas investigated include: async SQLModel configuration with PostgreSQL, many-to-many relationship patterns, Alembic migration setup, GitHub API integration for content management, and authorization abstraction patterns.

The standard approach is to use SQLModel with async sessions via asyncpg for high-performance database operations, PyGithub for GitHub API interactions (creating/updating files), webhooks for real-time sync (with polling as fallback), and a clean architecture with repository pattern allowing dual implementations (real PostgreSQL/GitHub and in-memory for testing).

**Primary recommendation:** Use async SQLModel with asyncpg for database operations, PyGithub for GitHub file operations, webhooks for sync with database queue, and strict repository pattern interfaces enabling real + in-memory implementations per CLAUDE.md requirements.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | latest | Web framework | Official template uses it, async-first, OpenAPI auto-generation |
| SQLModel | latest | ORM with Pydantic integration | Same author as FastAPI, combines Pydantic + SQLAlchemy |
| asyncpg | latest | Async PostgreSQL driver | Fastest Python PostgreSQL driver, native asyncio |
| psycopg2-binary | latest | Sync PostgreSQL driver | Required for some SQLAlchemy operations even in async context |
| Alembic | 1.18.1 | Database migrations | Standard SQLAlchemy migration tool, works with SQLModel |
| PyGithub | latest | GitHub API client | Full GitHub API coverage, file create/update/delete support |
| Pydantic | v2 | Data validation | Built into SQLModel, settings management |
| pydantic-settings | latest | Environment config | Official extension for .env file loading |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| greenlet | latest | Async SQLAlchemy support | Required dependency for async SQLModel |
| python-jose | latest | JWT handling | When implementing auth tokens |
| passlib | latest | Password hashing | When storing user passwords |
| httpx | latest | Async HTTP client | For webhook delivery verification |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyGithub | GitPython | GitPython requires git installed, good for local repos only |
| PyGithub | dulwich | Pure Python but slower, better for embedded use |
| asyncpg | psycopg3 | psycopg3 is newer but asyncpg has more production usage |
| uv | Poetry | Poetry more mature but uv is 10-100x faster (see Claude's Discretion) |

**Installation:**
```bash
# Using uv (recommended)
uv add fastapi sqlmodel asyncpg psycopg2-binary alembic pygithub pydantic-settings greenlet

# Using pip
pip install fastapi sqlmodel asyncpg psycopg2-binary alembic pygithub pydantic-settings greenlet
```

## Architecture Patterns

### Recommended Project Structure
Per CLAUDE.md DDD/Clean Architecture requirements:

```
backend/
├── src/
│   └── atlas/
│       ├── domain/                    # Pure business logic, no I/O
│       │   ├── entities/              # User, Team, Skill, MCP, Tool
│       │   ├── value_objects/         # Email, Username, etc.
│       │   ├── errors/                # Domain-specific exceptions
│       │   └── interfaces/            # Repository abstract classes
│       │       ├── user_repository.py
│       │       ├── team_repository.py
│       │       ├── catalog_repository.py
│       │       └── content_repository.py  # Git content interface
│       │
│       ├── application/               # Use cases, orchestration
│       │   ├── services/              # Business logic orchestration
│       │   ├── dtos/                  # Data transfer objects
│       │   └── contracts/             # Service interfaces
│       │
│       ├── adapters/                  # All I/O implementations
│       │   ├── postgresql/            # Real DB implementations
│       │   │   ├── repositories/
│       │   │   ├── models.py          # SQLModel table definitions
│       │   │   └── session.py         # Async session factory
│       │   ├── github/                # Real GitHub implementations
│       │   │   └── content_repository.py
│       │   └── in_memory/             # Test implementations
│       │       ├── repositories/
│       │       └── content_repository.py
│       │
│       └── entrypoints/               # HTTP routes, CLI
│           ├── api/
│           │   ├── routes/
│           │   └── dependencies.py
│           └── cli/
│
├── migrations/                        # Alembic migrations
│   ├── versions/
│   └── env.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/                      # Same tests for all implementations
├── alembic.ini
└── pyproject.toml
```

### Pattern 1: Async Database Session Management
**What:** Async session factory with proper connection pooling
**When to use:** All database operations in FastAPI
**Example:**
```python
# Source: TestDriven.io + SQLModel docs
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/atlas"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL logging in dev
    future=True,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Critical: prevents implicit I/O
)

async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
```

### Pattern 2: Repository Pattern with Dual Implementations
**What:** Abstract repository interface with real and in-memory implementations
**When to use:** All data access operations
**Example:**
```python
# Source: CLAUDE.md + Cosmic Python patterns
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

# domain/interfaces/user_repository.py
class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def save(self, user: User) -> User:
        raise NotImplementedError

# adapters/postgresql/repositories/user_repository.py
class PostgresUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        statement = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

# adapters/in_memory/repositories/user_repository.py
class InMemoryUserRepository(AbstractUserRepository):
    def __init__(self):
        self._users: dict[UUID, User] = {}

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self._users.get(user_id)
```

### Pattern 3: Many-to-Many Relationships with Link Tables
**What:** SQLModel pattern for M2M relationships like User-Team
**When to use:** Users belonging to multiple teams
**Example:**
```python
# Source: SQLModel docs - many-to-many
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import UUID, uuid4

class UserTeamLink(SQLModel, table=True):
    """Link table for User-Team many-to-many relationship."""
    __tablename__ = "user_team_links"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    team_id: UUID = Field(foreign_key="teams.id", primary_key=True)
    role: str = Field(default="member")  # Extra field on link table
    joined_at: datetime = Field(default_factory=datetime.utcnow)

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)

    teams: list["Team"] = Relationship(
        back_populates="members",
        link_model=UserTeamLink,
    )

class Team(SQLModel, table=True):
    __tablename__ = "teams"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)

    members: list[User] = Relationship(
        back_populates="teams",
        link_model=UserTeamLink,
    )
```

### Pattern 4: Authorization Abstraction
**What:** Permission checking functions that can evolve from permissive to strict
**When to use:** All resource access checks
**Example:**
```python
# Source: Clean architecture RBAC patterns
from abc import ABC, abstractmethod

# domain/interfaces/authorization.py
class AbstractAuthorizationService(ABC):
    @abstractmethod
    async def can_view_skill(self, user: User, skill: Skill) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def can_edit_skill(self, user: User, skill: Skill) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def can_delete_skill(self, user: User, skill: Skill) -> bool:
        raise NotImplementedError

# adapters/authorization/permissive.py (Phase 1 implementation)
class PermissiveAuthorizationService(AbstractAuthorizationService):
    """Phase 1: Allow everything, structure in place for future RBAC."""

    async def can_view_skill(self, user: User, skill: Skill) -> bool:
        return True  # TODO: Implement actual RBAC in later phase

    async def can_edit_skill(self, user: User, skill: Skill) -> bool:
        return True

    async def can_delete_skill(self, user: User, skill: Skill) -> bool:
        return True

# Future: adapters/authorization/rbac.py with actual permission logic
```

### Pattern 5: GitHub Content Repository
**What:** Abstract content storage with GitHub implementation
**When to use:** All content file operations (skills, MCPs, tools)
**Example:**
```python
# Source: PyGithub docs
from github import Github
from abc import ABC, abstractmethod

# domain/interfaces/content_repository.py
class AbstractContentRepository(ABC):
    @abstractmethod
    async def get_content(self, path: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    async def save_content(self, path: str, content: str, message: str) -> str:
        """Save content and return commit SHA."""
        raise NotImplementedError

# adapters/github/content_repository.py
class GitHubContentRepository(AbstractContentRepository):
    def __init__(self, token: str, repo_name: str):
        self._github = Github(token)
        self._repo = self._github.get_repo(repo_name)

    async def get_content(self, path: str) -> Optional[str]:
        try:
            content = self._repo.get_contents(path)
            return content.decoded_content.decode("utf-8")
        except Exception:
            return None

    async def save_content(self, path: str, content: str, message: str) -> str:
        try:
            # Try to update existing file
            existing = self._repo.get_contents(path)
            result = self._repo.update_file(
                path=path,
                message=message,
                content=content,
                sha=existing.sha,
            )
        except Exception:
            # Create new file
            result = self._repo.create_file(
                path=path,
                message=message,
                content=content,
            )
        return result["commit"].sha
```

### Anti-Patterns to Avoid
- **Direct database access in routes:** Always go through repository interfaces
- **Importing adapters in domain:** Domain layer must not know about PostgreSQL or GitHub
- **Sync database operations in async routes:** Always use async session methods
- **Hardcoded connection strings:** Use pydantic-settings for all configuration
- **Single implementation per interface:** Always create both real and in-memory versions

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Database migrations | Custom SQL scripts | Alembic | Version tracking, rollbacks, autogenerate |
| GitHub file operations | Direct REST API calls | PyGithub | Auth handling, pagination, error handling |
| Password hashing | Custom hash functions | passlib[bcrypt] | Security audited, timing-attack safe |
| Environment config | os.environ parsing | pydantic-settings | Type validation, .env support, nesting |
| UUID generation | random strings | uuid.uuid4() or UUID7 | Standardized, collision-resistant |
| Async connection pooling | Manual connection management | SQLAlchemy pool | Pool sizing, health checks, recycling |
| Webhook signature validation | Custom HMAC | GitHub's webhook helpers | Timing-safe comparison |

**Key insight:** Database migrations and GitHub integrations have many edge cases (constraint naming, rate limits, retries) that existing libraries handle. Custom solutions will miss these.

## Common Pitfalls

### Pitfall 1: Models Not Detected by Alembic
**What goes wrong:** `alembic revision --autogenerate` generates empty migrations or "detected removed table"
**Why it happens:** SQLModel.metadata doesn't contain models that haven't been imported
**How to avoid:** Import all models in `migrations/env.py` BEFORE setting `target_metadata`
**Warning signs:** Empty upgrade/downgrade functions, unexpected table drops
```python
# migrations/env.py - CORRECT
from atlas.adapters.postgresql.models import *  # Import ALL models first
from sqlmodel import SQLModel

target_metadata = SQLModel.metadata
```

### Pitfall 2: SQLModel Custom Types Not Recognized
**What goes wrong:** Generated migrations have incorrect type references
**Why it happens:** SQLModel uses custom SQL types that Alembic doesn't render by default
**How to avoid:** Add `user_module_prefix` to env.py configuration
**Warning signs:** Type errors when running migrations
```python
# migrations/env.py
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_as_batch=True,  # Also needed for SQLite
    user_module_prefix="sqlmodel.sql.sqltypes.",
)
```

### Pitfall 3: Async Session expire_on_commit Issues
**What goes wrong:** Accessing model attributes after commit raises errors or triggers implicit I/O
**Why it happens:** SQLAlchemy's default behavior expires objects after commit
**How to avoid:** Set `expire_on_commit=False` in session factory
**Warning signs:** "greenlet_spawn has not been called" errors, unexpected queries

### Pitfall 4: Missing Both Sync and Async Drivers
**What goes wrong:** Import errors or operations fail unexpectedly
**Why it happens:** SQLModel/SQLAlchemy needs sync driver for some operations even in async context
**How to avoid:** Install BOTH asyncpg AND psycopg2-binary
**Warning signs:** "No module named 'psycopg2'" in seemingly async code

### Pitfall 5: Webhook Delivery Missing Due to Server Downtime
**What goes wrong:** Git content and database metadata get out of sync
**Why it happens:** Webhooks aren't retried forever, and server might be down
**How to avoid:** Implement polling fallback, store webhooks in queue, add sync verification
**Warning signs:** Database references files that don't exist in git, or vice versa

### Pitfall 6: GitHub Rate Limits
**What goes wrong:** API calls start failing with 403 errors
**Why it happens:** GitHub has rate limits (5000/hour for authenticated, 60/hour for unauthenticated)
**How to avoid:** Use webhooks primarily, cache responses, implement exponential backoff
**Warning signs:** Intermittent failures, especially during high-traffic periods

### Pitfall 7: Circular Import with Repository Pattern
**What goes wrong:** Import errors when setting up dependency injection
**Why it happens:** Domain imports interface, adapter imports domain, entrypoint imports both
**How to avoid:** Use TYPE_CHECKING for type hints, lazy imports in DI container
**Warning signs:** ImportError mentioning partially initialized modules

## Code Examples

Verified patterns from official sources:

### Alembic Initialization with SQLModel
```python
# Source: Alembic docs + SQLModel community patterns
# Run: alembic init -t async migrations

# migrations/env.py additions
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# CRITICAL: Import models before metadata
from atlas.adapters.postgresql.models import *
from sqlmodel import SQLModel

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

# Naming convention for constraints
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
target_metadata.naming_convention = NAMING_CONVENTION


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        user_module_prefix="sqlmodel.sql.sqltypes.",
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
        user_module_prefix="sqlmodel.sql.sqltypes.",
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Catalog Item with Type Discriminator (Single Table)
```python
# Source: SQLAlchemy inheritance patterns
# Recommendation: Single table for catalog items - simpler queries, shared attributes
from enum import Enum
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class CatalogItemType(str, Enum):
    SKILL = "skill"
    MCP = "mcp"
    TOOL = "tool"

class CatalogItem(SQLModel, table=True):
    """Single table for all catalog items with type discriminator."""
    __tablename__ = "catalog_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    type: CatalogItemType = Field(index=True)
    name: str = Field(index=True)
    description: str = Field(default="")

    # Git reference
    git_path: str = Field(unique=True)  # e.g., "skills/my-skill.md"

    # Ownership
    author_id: UUID = Field(foreign_key="users.id")
    team_id: Optional[UUID] = Field(default=None, foreign_key="teams.id")

    # Metadata
    tags: str = Field(default="")  # JSON array as string, or use ARRAY type
    usage_count: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### FastAPI Dependency Injection Setup
```python
# Source: FastAPI docs + clean architecture patterns
from fastapi import Depends
from typing import Annotated

from atlas.adapters.postgresql.session import get_session, AsyncSession
from atlas.adapters.postgresql.repositories.user_repository import PostgresUserRepository
from atlas.adapters.authorization.permissive import PermissiveAuthorizationService
from atlas.domain.interfaces.user_repository import AbstractUserRepository
from atlas.domain.interfaces.authorization import AbstractAuthorizationService


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> AbstractUserRepository:
    return PostgresUserRepository(session)


async def get_authorization_service() -> AbstractAuthorizationService:
    return PermissiveAuthorizationService()


# Usage in routes
@router.get("/users/{user_id}")
async def get_user(
    user_id: UUID,
    repo: Annotated[AbstractUserRepository, Depends(get_user_repository)],
):
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Sync SQLAlchemy | Async SQLModel + asyncpg | 2023+ | 10x+ throughput for I/O bound ops |
| pip + requirements.txt | uv or Poetry | 2024+ | Faster installs, lock files, reproducibility |
| GitPython for GitHub | PyGithub for API | N/A (different use cases) | PyGithub for API ops, GitPython for local git |
| Polling for sync | Webhooks + queue | Best practice | Real-time updates, lower API usage |
| psycopg2 | asyncpg for async | 2020+ | Native async support, better performance |

**Deprecated/outdated:**
- `databases` library: SQLModel now has native async support
- Sync SQLAlchemy sessions with FastAPI: Use async sessions for proper async handling
- Manual constraint naming: Use naming_convention dict for consistent, migration-friendly names

## Open Questions

Things that couldn't be fully resolved:

1. **Catalog Item Entity Design: Separate Tables vs Single Table**
   - What we know: SQLAlchemy supports both single-table and joined-table inheritance
   - Single table: Simpler queries, no JOINs, but potential NULL columns
   - Separate tables: Cleaner schema, but complex polymorphic queries
   - **Recommendation:** Use single table with type discriminator - catalog items share most attributes (name, description, git_path, author, team, tags), type-specific data is minimal

2. **Git Sync Mechanism: Webhooks vs Polling**
   - What we know: Webhooks are preferred for real-time, polling as fallback
   - GitHub webhook limitations: 10-second response timeout, no guaranteed delivery
   - **Recommendation:** Webhooks primary with database queue for processing, daily polling sync as consistency check

3. **Python Package Manager: uv vs Poetry**
   - What we know: uv is 10-100x faster, Poetry is more mature
   - uv: Fast, single binary, manages Python versions too
   - Poetry: Stable, well-documented, larger community
   - **Recommendation:** Use uv for speed benefits in CI/CD, but either works. FastAPI official template uses uv.

4. **UUID Version for Primary Keys**
   - What we know: UUID4 is random, UUID7 is timestamp-ordered
   - UUID7: Better index performance due to sequential nature
   - **Recommendation:** Use UUID7 if available in your UUID library, otherwise UUID4 is fine

## Sources

### Primary (HIGH confidence)
- SQLModel documentation (https://sqlmodel.tiangolo.com/) - Many-to-many relationships, model definition
- Alembic 1.18.1 documentation (https://alembic.sqlalchemy.org/) - Migration commands, configuration
- FastAPI Full Stack Template (https://github.com/fastapi/full-stack-fastapi-template) - Project structure, stack decisions
- PyGithub documentation (https://pygithub.readthedocs.io/) - Repository operations, file CRUD
- SQLAlchemy 2.0 inheritance docs (https://docs.sqlalchemy.org/en/20/orm/inheritance.html) - Table inheritance patterns

### Secondary (MEDIUM confidence)
- TestDriven.io async SQLModel guide (https://testdriven.io/blog/fastapi-sqlmodel/) - Async session setup, Alembic configuration
- fastapi-alembic-sqlmodel-async template (https://github.com/jonra1993/fastapi-alembic-sqlmodel-async) - Production patterns
- ivan-borovets/fastapi-clean-example (https://github.com/ivan-borovets/fastapi-clean-example) - Clean architecture with FastAPI
- GitHub webhooks documentation (https://docs.github.com/en/webhooks) - Webhook setup and best practices

### Tertiary (LOW confidence)
- Various Medium/DEV articles on uv vs Poetry - Package manager comparison
- WebSearch results on RBAC patterns - Authorization abstraction approaches

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official docs and templates confirm all choices
- Architecture: HIGH - Clean architecture patterns well-documented, CLAUDE.md provides clear requirements
- Pitfalls: HIGH - Multiple sources confirm common issues with SQLModel+Alembic
- GitHub integration: MEDIUM - PyGithub well-documented but async patterns less clear
- Authorization abstraction: MEDIUM - Patterns clear but implementation details are project-specific

**Research date:** 2025-01-23
**Valid until:** 60 days (stable libraries, mature patterns)
