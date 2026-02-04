# Axent Lite

Git-only sync for Claude configuration. No backend required.

## What it does

Syncs skills, MCPs, and tools from a Git repository directly to `~/.claude/`. Perfect for teams that want to share Claude configurations without running a full Axent backend.

## Installation

```bash
pip install git+https://github.com/sarfati7/atlas.git#subdirectory=atlas-lite
```

Or just download the single file:

```bash
curl -o axent-lite https://raw.githubusercontent.com/sarfati7/atlas/main/atlas-lite/atlas_lite.py
chmod +x axent-lite
```

## Usage

```bash
# 1. Point to your team's Git repo
axent-lite init https://github.com/yourcompany/claude-catalog.git

# 2. Sync to ~/.claude/
axent-lite sync

# 3. Push local skills to repo
axent-lite push

# 4. Check status anytime
axent-lite status

# Preview changes without syncing
axent-lite sync --dry-run
```

## Repository Structure

Your Git repo should look like this:

```
CLAUDE.md              # Optional: shared base configuration
skills/
  my-skill/
    SKILL.md           # Skill documentation
    config.yaml        # Optional: metadata
mcps/
  my-mcp/
    README.md
    config.yaml
tools/
  my-tool/
    README.md
    config.yaml
```

## How it works

1. Clones/pulls your Git repo to `~/.cache/axent-lite/repo`
2. Copies files to `~/.claude/`:
   - `CLAUDE.md` → `~/.claude/CLAUDE.md` (only with `--include-config`)
   - `skills/*` → `~/.claude/skills/*`
   - `mcps/*` → `~/.claude/commands/*`
   - `tools/*` → `~/.claude/tools/*`
3. Only updates files that changed (compares hashes)
4. Never deletes local files (safe to have local-only configs)

## Requirements

- Python 3.10+
- Git installed
- No other dependencies (uses stdlib only)

## Configuration

Config stored in `~/.axent-lite.json`:

```json
{
  "repo_url": "https://github.com/yourcompany/claude-catalog.git",
  "last_sync": "abc1234"
}
```

## vs Full Axent

| Feature | Axent Lite | Full Axent |
|---------|-----------|-----------|
| Browse catalog UI | ✗ | ✓ |
| Search/filter | ✗ | ✓ |
| User profiles | ✗ | ✓ |
| Config inheritance | ✗ | ✓ |
| Version history UI | ✗ | ✓ |
| Admin panel | ✗ | ✓ |
| Setup complexity | Just Git | Backend + DB |
| Dependencies | None | PostgreSQL, etc |

Axent Lite is for teams that want simplicity. Full Axent is for organizations that need visibility, governance, and a web UI.
