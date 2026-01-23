# Atlas

## What This Is

An agent management platform for companies using AI agents (like Claude Code). Developers can discover all skills, MCPs, and tools available at their company, create their agent profile, edit their claude.md through a web UI, and sync configurations to their local Claude instance via CLI.

## Core Value

A new developer can onboard in minutes instead of weeks by seeing everything their team has built — no more asking around in Slack to discover what skills and MCPs exist.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Developer can browse all skills, MCPs, and tools available company-wide
- [ ] Developer can view documentation and details for each skill/MCP/tool
- [ ] Developer can create and edit their agent profile (claude.md) through the web UI
- [ ] Developer can sync their profile to local Claude instance via CLI
- [ ] Admin can manage teams through admin panel
- [ ] Admin can manage users through admin panel
- [ ] Git repo stores actual skill/MCP/tool files as source of truth
- [ ] Database stores metadata, user profiles, and team structure
- [ ] MCP server backend for communication

### Out of Scope

- Team-scoped visibility (see only your team's stuff) — v1 shows everything to everyone
- Role-based access control (non-admin users) — v1 all users are admins
- Context-aware initialization (auto-suggest based on Monday ticket) — future enhancement
- Monday/Slack/docs integrations — the dogfooding system is future scope
- R&D lead analytics dashboard (usage, adoption, duplication) — future scope
- Skill marketplace / forking mechanism — future scope

## Context

**Problem space:** Companies developing with agentic workspaces lack control over their agents, skills, MCPs, and tools. This manifests as:
- Developers duplicating effort (building the same skill twice)
- No visibility into what tools are being used across teams
- New developers spending weeks discovering what exists
- No awareness of new skills or MCPs teammates have built
- Security/compliance blindness about connected MCPs

**User scenario:** Roy joins a company that's been working all year. Instead of spending weeks asking around to understand what skills, MCPs, and tools his team uses, he opens Atlas, sees everything organized in a UI, creates his agent profile, and syncs to his local Claude.

**Future vision:** The platform will eventually dogfood itself — using MCPs connected to Monday, Slack, and documentation to automatically suggest relevant configurations based on what ticket a developer is working on. R&D leads will have visibility into adoption, duplication, and compliance. But v1 focuses on the single-user discovery and sync flow.

## Constraints

- **Tech stack**: React frontend, Python backend, PostgreSQL database, MCP server for communication
- **Data architecture**: Git repo holds actual skill/MCP/tool files; database holds metadata, user profiles, team structure
- **Sync mechanism**: CLI command copies from git repo to user's local `~/.claude/`
- **Access model (v1)**: All users see everything, all users are admins

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Git repo as file source of truth | Skills/MCPs/tools are code — git is natural for versioning and collaboration | — Pending |
| MCP server backend | Easy communication pattern, aligns with the domain (managing MCPs) | — Pending |
| All users as admins for v1 | Simplifies v1 scope, role-based access added later | — Pending |
| Show everything to everyone for v1 | Team scoping adds complexity, defer to v2 | — Pending |
| PostgreSQL over SQLite | Multi-user platform needs proper relational DB, good Python ecosystem | — Pending |

---
*Last updated: 2025-01-23 after initialization*
