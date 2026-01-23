# Stack Research

**Domain:** Agent Management Platform (React + Python + MCP)
**Researched:** 2026-01-23
**Confidence:** HIGH

## Recommended Stack

### Frontend Core

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| React | 19.2 | UI framework | Latest stable with Activity API, useEffectEvent, improved Suspense batching. React 19.2 released October 2025. |
| TypeScript | 5.6+ | Type safety | Industry standard for React apps. Full support in all tooling. |
| Vite | 7.3.1 | Build tool | CRA is deprecated. Vite is the official recommendation for React. 5x faster full builds, 100x faster incremental. |
| Tailwind CSS | 4.0+ | Styling | Single import setup, automatic content detection, 100x faster incremental builds. Requires Safari 16.4+, Chrome 111+, Firefox 128+. |

### Frontend State & Data

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| TanStack Query | 5.90+ | Server state | De facto standard for data fetching. Caching, background refetch, optimistic updates. 80% of server-state patterns. |
| Zustand | 5.0.10 | Client state | Simple, no Provider needed, 40% adoption in 2025. Perfect complement to TanStack Query. |

### Frontend UI Components

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| shadcn/ui | latest | Component library | 100k+ GitHub stars. Copy-paste components, full control, no lock-in. Built on Radix + Tailwind. |
| Radix UI | latest | Headless primitives | Accessibility built-in. Foundation for shadcn/ui. |
| Lucide React | latest | Icons | Modern icon set, tree-shakeable, consistent with shadcn/ui. |

### Backend Core

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12+ | Runtime | FastAPI requires 3.9+. Use 3.12 for performance improvements and better typing. |
| FastAPI | 0.128.0 | API framework | 6x faster than Django. Native async, automatic OpenAPI docs, type validation via Pydantic. Ideal for AI-driven apps and microservices. |
| Pydantic | 2.12.5 | Data validation | Core dependency of FastAPI. Type-safe validation, serialization, Python 3.14 support. |
| Uvicorn | latest | ASGI server | Standard production server for FastAPI. |

### MCP Server

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| mcp (Python SDK) | 1.25.0 | MCP protocol | Official Anthropic SDK. Stable v1.x recommended for production (v2 expected Q1 2026). |
| FastMCP | 2.x (stable) | High-level MCP | Pythonic decorator-based MCP server creation. Pin to v2 for production (v3 in beta). |

### Database & ORM

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| PostgreSQL | 16+ | Primary database | Robust, reliable, excellent ecosystem. Supports JSON, full-text search, concurrent connections. |
| SQLModel | 0.0.31 | ORM | By FastAPI creator. Combines SQLAlchemy + Pydantic. Perfect FastAPI integration, reduced boilerplate. |
| SQLAlchemy | 2.0+ | SQL toolkit | Powers SQLModel. Use directly for complex queries. |
| Alembic | latest | Migrations | Standard for SQLAlchemy migrations. Async template available. |
| asyncpg | 0.31.0 | Async driver | 5x faster than psycopg3. Use for high-performance async PostgreSQL. |

### Authentication

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| python-jose | latest | JWT handling | HS256/RS256 token encoding/decoding. FastAPI docs recommend this. |
| passlib | latest | Password hashing | bcrypt hashing, secure password verification. |
| OAuth2PasswordBearer | (FastAPI) | Token extraction | Built into FastAPI security module. |

### CLI Tool

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Typer | 0.21.1 | CLI framework | FastAPI of CLIs. Type hints, auto-completion, built on Click. Same author as FastAPI. |
| Rich | latest | Terminal output | Beautiful formatting, tables, progress bars. Bundled with Typer. |

### Testing

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Vitest | latest | Frontend testing | 10x faster than Jest. Native ESM, Vite integration. Use with React Testing Library. |
| React Testing Library | latest | Component testing | User-focused testing, accessibility-aware. |
| pytest | latest | Backend testing | Standard Python testing. Async support via pytest-asyncio. |
| pytest-asyncio | latest | Async testing | Required for testing FastAPI async endpoints. |
| httpx | latest | HTTP client | Async HTTP for testing FastAPI with TestClient. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv | Python package manager | Fast Rust-based pip replacement. Recommended by FastAPI docs. |
| pnpm | Node package manager | Faster than npm, efficient disk usage. |
| ESLint + Prettier | Code quality | Standard for React/TS projects. |
| Ruff | Python linting | Fast Rust-based linter, replaces flake8 + black + isort. |
| Docker | Containerization | Standard for deployment. |

## Installation

### Frontend

```bash
# Create project with Vite
pnpm create vite@latest frontend --template react-swc-ts
cd frontend

# Core
pnpm add react@^19.2 react-dom@^19.2

# State & Data
pnpm add @tanstack/react-query@^5 zustand@^5

# UI (shadcn/ui installed via CLI)
pnpm dlx shadcn-ui@latest init

# Routing
pnpm add react-router-dom@^7

# Dev dependencies
pnpm add -D vitest @testing-library/react @testing-library/jest-dom jsdom
pnpm add -D tailwindcss@^4 @tailwindcss/vite
pnpm add -D typescript @types/react @types/react-dom
pnpm add -D eslint prettier eslint-plugin-react-hooks
```

### Backend

```bash
# Using uv (recommended)
uv init backend
cd backend

# Core
uv add fastapi[standard] uvicorn[standard] pydantic

# Database
uv add sqlmodel sqlalchemy[asyncio] alembic asyncpg

# MCP
uv add mcp  # Official SDK

# Authentication
uv add "python-jose[cryptography]" "passlib[bcrypt]" python-multipart

# CLI
uv add typer[all]  # Includes rich

# Testing
uv add --dev pytest pytest-asyncio httpx pytest-cov
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| FastAPI | Django REST Framework | Need built-in admin panel, complex relational data, existing Django expertise. DRF has 30min admin setup vs 2-3 days in FastAPI. |
| SQLModel | Prisma Python | Need introspection from existing DB, working with multiple database types (MySQL, Mongo). 3x faster introspection than SQLAlchemy. |
| SQLModel | Raw SQLAlchemy | Complex queries, need full ORM control, existing SQLAlchemy codebase. |
| asyncpg | psycopg3 | Need unified sync/async API, Row Factories for Pydantic mapping, more Pythonic experience. |
| TanStack Query | SWR | Simpler needs, smaller bundle size, Vercel ecosystem preference. |
| Zustand | Redux Toolkit | Large enterprise app, multiple teams, need strict patterns and devtools. |
| shadcn/ui | MUI (Material UI) | Need Material Design, prefer opinionated component library, faster initial setup. |
| Vite | Next.js | Need SSR, static generation, API routes in same project, SEO-critical public-facing app. |
| Vitest | Jest | React Native app, legacy codebase, need Jest ecosystem plugins. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Create React App (CRA) | Officially deprecated Feb 2025. Slow builds, outdated configs. | Vite |
| Flask | Not async-native, manual validation, no automatic docs. | FastAPI |
| Django (for API-only) | Overkill for API-first architecture, slower performance. | FastAPI |
| psycopg2 | Sync only, older API. | asyncpg or psycopg3 |
| Moment.js | Deprecated, large bundle. | date-fns or dayjs |
| Redux (without Toolkit) | Too much boilerplate, complex setup. | Zustand or Redux Toolkit |
| Jest (for Vite projects) | Slow, requires complex ESM config. | Vitest |
| Tailwind CSS v3 | v4 is significantly faster with simpler setup. | Tailwind CSS v4 |
| MCP SDK v2 beta | Not stable yet, v2 expected Q1 2026. | MCP SDK v1.x |
| FastMCP v3 beta | In beta, breaking changes likely. | FastMCP v2.x |

## Stack Patterns by Variant

**If building for maximum performance:**
- Use asyncpg directly (skip SQLModel for hot paths)
- Use React Server Components with TanStack Query
- Consider edge deployment

**If team has Django experience:**
- SQLModel will feel familiar (models work like Django)
- FastAPI patterns similar to DRF viewsets
- Consider Django admin as separate internal tool

**If MCP server needs SSE transport:**
- Use `mcp.run(transport="sse")` for remote access
- For STDIO transport, never write to stdout (breaks JSON-RPC)

**If authentication needs enterprise SSO:**
- Add axioms-fastapi for AWS Cognito/Auth0/Okta integration
- Use RS256 over HS256 for larger systems

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| React 19.2 | TanStack Query 5.90+ | React Query v5 requires React 18+ (uses useSyncExternalStore) |
| FastAPI 0.128.0 | Pydantic 2.x | Supports both v1 and v2 models simultaneously |
| SQLModel 0.0.31 | SQLAlchemy 2.0+ | Based on SQLAlchemy 2.0 |
| Vite 7.3.1 | Tailwind 4.0 | First-party Vite plugin available |
| Tailwind 4.0 | Modern browsers only | Safari 16.4+, Chrome 111+, Firefox 128+ |
| MCP SDK 1.25.0 | Python 3.10+ | Official requirement |
| Vitest latest | Vite 7.x | Native integration |

## Sources

### HIGH Confidence (Official Documentation)
- [React Versions](https://react.dev/versions) - React 19.2 release info
- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/) - FastAPI 0.128.0
- [Vite Releases](https://vite.dev/releases) - Vite 7.3.1
- [TanStack Query npm](https://www.npmjs.com/package/@tanstack/react-query) - v5.90.19
- [Tailwind CSS v4.0](https://tailwindcss.com/blog/tailwindcss-v4) - Major release
- [MCP Python SDK GitHub](https://github.com/modelcontextprotocol/python-sdk) - v1.25.0, v2 roadmap
- [Pydantic Releases](https://github.com/pydantic/pydantic/releases) - v2.12.5
- [SQLModel GitHub](https://github.com/fastapi/sqlmodel) - v0.0.31
- [Typer](https://typer.tiangolo.com/) - v0.21.1
- [asyncpg PyPI](https://pypi.org/project/asyncpg/) - v0.31.0

### MEDIUM Confidence (Verified Community Sources)
- [Better Stack: Django vs FastAPI](https://betterstack.com/community/guides/scaling-python/django-vs-fastapi/) - Performance benchmarks
- [React State Management 2025](https://www.developerway.com/posts/react-state-management-2025) - Zustand + TanStack Query patterns
- [shadcn/ui](https://ui.shadcn.com/) - Component library approach
- [Vitest vs Jest comparison](https://dev.to/saswatapal/why-i-chose-vitest-over-jest-10x-faster-tests-native-esm-support-13g6) - Performance benchmarks
- [FastMCP GitHub](https://github.com/jlowin/fastmcp) - v2/v3 status

### LOW Confidence (Needs Validation)
- Prisma Python 3x faster introspection claim (single source benchmark)
- asyncpg 5x faster than psycopg3 (2023 benchmark, may be outdated)

---
*Stack research for: Atlas Agent Management Platform*
*Researched: 2026-01-23*
