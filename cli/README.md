# Atlas CLI

Command-line tool to sync Claude configuration from the Atlas platform to your local `~/.claude/` directory.

## Installation

```bash
pip install git+https://github.com/sarfati7/atlas.git#subdirectory=cli
```

That's it. The `atlas` command is now available.

## Usage

### Authentication

```bash
# Log in to Atlas
atlas auth login

# Check authentication status
atlas auth status

# Log out
atlas auth logout
```

### Syncing Configuration

```bash
# Sync configuration from Atlas to ~/.claude/CLAUDE.md
atlas sync

# Preview what would be synced (dry run)
atlas sync --dry-run

# Force sync even if local file exists
atlas sync --force
```

### Status and Diagnostics

```bash
# Quick sync status (local vs remote)
atlas status

# Full health check
atlas doctor
```

## Configuration

### API URL

By default, the CLI connects to `http://localhost:8000/api/v1`. Override with:

```bash
export ATLAS_API_URL=https://atlas.yourcompany.com/api/v1
```

### CI/Headless Systems

On systems without a graphical keyring (CI, servers), use environment variables:

```bash
export ATLAS_ACCESS_TOKEN=your_token_here
atlas sync
```

## Troubleshooting

### "No recommended backend" error

This means keyring can't find a secure storage backend. Options:

1. Install a keyring backend (e.g., `secretstorage` on Linux)
2. Use `ATLAS_ACCESS_TOKEN` environment variable

### Network errors

Run `atlas doctor` to check connectivity to the Atlas API.

## Development

```bash
# Clone and install in development mode
cd cli
uv sync
uv pip install -e .

# Install dev dependencies
uv sync --dev

# Run tests
uv run python -m pytest

# Run CLI in development
uv run atlas --help
```
