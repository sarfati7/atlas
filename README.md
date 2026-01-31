# Atlas

Agent management platform for teams using AI coding assistants like Claude Code. Discover skills, MCPs, and tools available at your company, edit your configuration through a web UI, and sync to your local Claude instance.

## Quick Start

### Option 1: Full Platform (Web UI + Backend)

For teams that want a full catalog UI, user management, and governance.

```bash
# Backend
cd backend
cp .env.example .env  # Configure DATABASE_URL, GITHUB_TOKEN, etc.
uv sync
uv run alembic upgrade head
uv run uvicorn atlas.entrypoints.app:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Option 2: Atlas Lite (Git-only)

For teams that just want to share configs via Git. No backend required.

```bash
pip install git+https://github.com/sarfati7/atlas.git#subdirectory=atlas-lite

atlas-lite init https://github.com/yourcompany/claude-catalog.git
atlas-lite sync
```

See [atlas-lite/README.md](atlas-lite/README.md) for details.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  PostgreSQL │
│   (React)   │     │  (FastAPI)  │     │             │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   GitHub    │
                    │  (catalog)  │
                    └─────────────┘
```

- **Frontend**: React + Vite + TanStack Query + shadcn/ui
- **Backend**: Python + FastAPI + SQLAlchemy
- **Database**: PostgreSQL (metadata, users, teams)
- **Storage**: GitHub repository (skills, MCPs, tools content)

## CLI Tool

Sync your configuration from Atlas to `~/.claude/`:

```bash
pip install git+https://github.com/sarfati7/atlas.git#subdirectory=cli

atlas auth login
atlas sync           # Sync CLAUDE.md
atlas push           # Upload local skills/MCPs/tools
atlas pull           # Download from Atlas
atlas status         # Check sync status
atlas doctor         # Diagnostics
```

## Project Structure

```
atlas/
├── backend/         # FastAPI backend
├── frontend/        # React frontend
├── cli/             # Full CLI (requires backend)
└── atlas-lite/      # Standalone Git-only sync
```

## Features

- **Catalog Browser**: Search and filter skills, MCPs, and tools
- **Configuration Editor**: Edit claude.md with Monaco editor
- **Version History**: View and rollback configuration changes
- **Team Management**: Create teams, manage members
- **User Management**: Roles, permissions, audit logs
- **CLI Sync**: Push/pull configurations to local machine

## License

MIT
