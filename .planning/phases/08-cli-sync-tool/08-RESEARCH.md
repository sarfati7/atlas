# Phase 8: CLI Sync Tool - Research

**Researched:** 2026-01-25
**Domain:** Python CLI Development, Authentication, Cross-Platform File Operations
**Confidence:** HIGH

## Summary

This research covers building a CLI tool that syncs user configuration from the Atlas platform to local `~/.claude/` directory. The CLI needs to authenticate with the backend API, securely store credentials, and perform atomic file operations across macOS, Linux, and Windows.

The standard Python CLI stack in 2025/2026 uses **Typer** for command-line interface (built on Click, from the same author as FastAPI), **httpx** for HTTP requests (supports both sync and async), **keyring** for cross-platform secure credential storage, and **Rich** for beautiful terminal output. This stack is well-established, actively maintained, and provides excellent developer experience.

For atomic file operations, the deprecated `atomicwrites` library is replaced by Python's built-in `tempfile` module combined with `os.replace()` - this is the recommended approach per the atomicwrites maintainer.

**Primary recommendation:** Use Typer + httpx + keyring + Rich stack with stdlib tempfile/os.replace for atomic writes. Structure as a separate `cli/` directory in the monorepo with its own pyproject.toml.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| typer | latest (0.9+) | CLI framework | Type hints, auto-help, auto-completion, same author as FastAPI |
| httpx | 0.27+ | HTTP client | Sync/async support, connection pooling, modern API |
| keyring | 25.7+ | Credential storage | Cross-platform (macOS Keychain, Windows Credential Locker, Linux Secret Service) |
| rich | 14.3+ | Console output | Tables, progress bars, colors, status indicators |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pathlib | stdlib | Path handling | All file path operations (cross-platform) |
| tempfile | stdlib | Temp files | Atomic write pattern |
| shellingham | auto-installed | Shell detection | Typer auto-completion |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Typer | Click | Typer is built on Click but adds type hints, modern API - prefer Typer |
| httpx | requests | httpx has async support and HTTP/2 - prefer httpx for modern apps |
| keyring | manual file storage | Keyring uses OS-native secure storage - never hand-roll credential storage |
| Rich | print() | Rich provides progress bars, tables, colors - worth the dependency |

**Installation:**
```bash
uv add typer httpx keyring rich
```

## Architecture Patterns

### Recommended Project Structure
```
cli/
├── pyproject.toml           # Separate package with CLI entry point
├── src/
│   └── atlas_cli/
│       ├── __init__.py      # Version, package info
│       ├── main.py          # Typer app definition, command groups
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── auth.py      # login, logout, status commands
│       │   ├── sync.py      # sync command (main functionality)
│       │   └── doctor.py    # doctor, config commands
│       ├── api/
│       │   ├── __init__.py
│       │   ├── client.py    # HTTP client wrapper with auth
│       │   └── auth.py      # Custom httpx.Auth for token refresh
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── credentials.py  # Keyring wrapper
│       │   └── files.py        # Atomic file operations
│       └── console.py       # Rich console utilities
└── tests/
    └── ...
```

### Pattern 1: Typer Application with Commands
**What:** Define main app and register commands from modules
**When to use:** Always - this is the standard Typer pattern
**Example:**
```python
# Source: https://typer.tiangolo.com/
# main.py
import typer
from atlas_cli.commands import auth, sync, doctor

app = typer.Typer(
    name="atlas",
    help="Sync Claude configuration from Atlas platform",
    no_args_is_help=True,
)

# Register command groups
app.add_typer(auth.app, name="auth")
app.command()(sync.sync)
app.command()(doctor.doctor)

def main():
    app()
```

### Pattern 2: httpx Client with Base URL and Auth
**What:** Reusable HTTP client with configured base URL and authentication
**When to use:** All API calls
**Example:**
```python
# Source: https://www.python-httpx.org/advanced/clients/
# api/client.py
import httpx
from atlas_cli.api.auth import TokenAuth
from atlas_cli.storage.credentials import get_access_token

def create_client() -> httpx.Client:
    """Create configured HTTP client."""
    return httpx.Client(
        base_url="https://api.atlas.example.com/api/v1",
        auth=TokenAuth(),
        headers={"User-Agent": "atlas-cli/0.1.0"},
        timeout=30.0,
    )
```

### Pattern 3: Custom Auth with Token Refresh
**What:** httpx.Auth subclass that handles token refresh automatically
**When to use:** When access tokens expire and need refresh
**Example:**
```python
# Source: https://www.python-httpx.org/advanced/authentication/
# api/auth.py
import httpx
from atlas_cli.storage.credentials import (
    get_access_token, get_refresh_token,
    save_access_token
)

class TokenAuth(httpx.Auth):
    requires_response_body = True

    def __init__(self):
        self.access_token = get_access_token()
        self.refresh_token = get_refresh_token()

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.access_token}"
        response = yield request

        if response.status_code == 401 and self.refresh_token:
            # Token expired, refresh it
            refresh_request = httpx.Request(
                "POST",
                request.url.copy_with(path="/api/v1/auth/refresh"),
                cookies={"refresh_token": self.refresh_token},
            )
            refresh_response = yield refresh_request

            if refresh_response.status_code == 200:
                data = refresh_response.json()
                self.access_token = data["access_token"]
                save_access_token(self.access_token)

                # Retry original request
                request.headers["Authorization"] = f"Bearer {self.access_token}"
                yield request
```

### Pattern 4: Keyring Credential Storage
**What:** Store tokens securely using OS keychain
**When to use:** All credential storage
**Example:**
```python
# Source: https://keyring.readthedocs.io/en/stable/
# storage/credentials.py
import keyring

SERVICE_NAME = "atlas-cli"

def save_tokens(access_token: str, refresh_token: str) -> None:
    """Store tokens in system keychain."""
    keyring.set_password(SERVICE_NAME, "access_token", access_token)
    keyring.set_password(SERVICE_NAME, "refresh_token", refresh_token)

def get_access_token() -> str | None:
    """Retrieve access token from keychain."""
    return keyring.get_password(SERVICE_NAME, "access_token")

def get_refresh_token() -> str | None:
    """Retrieve refresh token from keychain."""
    return keyring.get_password(SERVICE_NAME, "refresh_token")

def clear_tokens() -> None:
    """Remove all stored tokens."""
    try:
        keyring.delete_password(SERVICE_NAME, "access_token")
        keyring.delete_password(SERVICE_NAME, "refresh_token")
    except keyring.errors.PasswordDeleteError:
        pass  # Already deleted
```

### Pattern 5: Atomic File Write
**What:** Write to temp file, then atomic rename
**When to use:** Writing configuration to ~/.claude/
**Example:**
```python
# Source: https://docs.python.org/3/library/tempfile.html
# storage/files.py
import os
import tempfile
from pathlib import Path

def atomic_write(path: Path, content: str) -> None:
    """Write content atomically - either fully succeeds or no change."""
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file in same directory (same filesystem for atomic rename)
    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=".tmp_",
        suffix=path.suffix,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # Ensure written to disk

        # Atomic rename (same filesystem)
        os.replace(tmp_path, path)
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
```

### Pattern 6: Cross-Platform Home Directory
**What:** Use pathlib.Path.home() for ~/.claude/
**When to use:** Determining config directory
**Example:**
```python
# Source: https://docs.python.org/3/library/pathlib.html
from pathlib import Path

def get_claude_dir() -> Path:
    """Get ~/.claude/ directory path (cross-platform)."""
    return Path.home() / ".claude"

def get_config_path() -> Path:
    """Get path to CLAUDE.md config file."""
    return get_claude_dir() / "CLAUDE.md"
```

### Anti-Patterns to Avoid
- **String concatenation for paths:** Use `pathlib.Path` with `/` operator instead
- **Storing tokens in plain text files:** Use `keyring` for OS-native secure storage
- **Direct file write without atomicity:** Always write-to-temp-then-rename
- **Hardcoding API URLs:** Use configuration or environment variables
- **Creating httpx.Client per request:** Reuse client for connection pooling

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Secure credential storage | Encrypted file | `keyring` | OS-native security, no crypto bugs |
| CLI argument parsing | argparse loops | `typer` | Auto-help, completion, type validation |
| Progress indicators | print with \r | `rich.progress` | Handles terminal quirks, looks professional |
| HTTP client | urllib | `httpx` | Connection pooling, auth, timeouts |
| Atomic file writes | try/except rename | tempfile + os.replace | Race conditions, cross-platform issues |
| Path handling | string manipulation | `pathlib` | Windows/Unix differences handled |
| Terminal colors | ANSI codes | `rich.console` | Terminal capability detection |

**Key insight:** CLI tools have many edge cases (terminals, platforms, interruptions). These libraries have years of bug fixes for scenarios you won't anticipate.

## Common Pitfalls

### Pitfall 1: Token Storage in Plain Files
**What goes wrong:** Credentials stored in `~/.atlas/token.txt` are readable by any process
**Why it happens:** Seems simpler than keychain integration
**How to avoid:** Always use `keyring` - it's only 3 function calls
**Warning signs:** Any file I/O for tokens, chmod operations

### Pitfall 2: Non-Atomic Config Writes
**What goes wrong:** Sync interrupted mid-write leaves corrupt `CLAUDE.md`
**Why it happens:** Direct file.write() without temp file pattern
**How to avoid:** Always use atomic_write() pattern with tempfile + os.replace
**Warning signs:** Using open() directly for config writes

### Pitfall 3: Windows Path Handling
**What goes wrong:** Hardcoded `/` separators, `~` expansion fails
**Why it happens:** Development on macOS/Linux only
**How to avoid:** Use `pathlib.Path` exclusively, `Path.home()` for home dir
**Warning signs:** String concatenation with "/" for paths

### Pitfall 4: No Error Handling for Network Issues
**What goes wrong:** Cryptic httpx exceptions bubble up to user
**Why it happens:** Happy path development
**How to avoid:** Catch httpx.RequestError and httpx.HTTPStatusError, show friendly messages
**Warning signs:** Raw exception tracebacks in CLI output

### Pitfall 5: Token Expiry Not Handled
**What goes wrong:** User gets 401 errors, has to re-login constantly
**Why it happens:** Forgot to implement refresh flow
**How to avoid:** Implement TokenAuth class with refresh logic (Pattern 3)
**Warning signs:** Commands failing with "unauthorized" after short time

### Pitfall 6: Sync Not Idempotent
**What goes wrong:** Running sync twice causes issues
**Why it happens:** Not checking if content already matches
**How to avoid:** Compare content before write, report "already up to date"
**Warning signs:** Sync always reports success even when unchanged

### Pitfall 7: No Keyring Backend on Headless Linux
**What goes wrong:** keyring fails with "No recommended backend" on servers
**Why it happens:** No graphical keyring daemon (GNOME, KDE) running
**How to avoid:** Detect and provide fallback with clear error message, recommend `--store-file` flag for CI/servers
**Warning signs:** Works on dev machine, fails in CI

## Code Examples

Verified patterns from official sources:

### Login Command
```python
# commands/auth.py
import typer
import httpx
from rich.console import Console
from atlas_cli.storage.credentials import save_tokens, clear_tokens

app = typer.Typer()
console = Console()

@app.command()
def login(
    email: str = typer.Option(..., prompt=True, help="Your Atlas email"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Your password"),
):
    """Authenticate with Atlas platform."""
    with console.status("Authenticating..."):
        try:
            response = httpx.post(
                "https://api.atlas.example.com/api/v1/auth/login",
                data={"username": email, "password": password},  # OAuth2 form
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()
            # Note: refresh token comes from Set-Cookie header
            refresh_token = response.cookies.get("refresh_token", "")

            save_tokens(data["access_token"], refresh_token)
            console.print("[green]Successfully logged in![/green]")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                console.print("[red]Invalid email or password[/red]")
            else:
                console.print(f"[red]Login failed: {e.response.text}[/red]")
            raise typer.Exit(1)
        except httpx.RequestError as e:
            console.print(f"[red]Network error: {e}[/red]")
            raise typer.Exit(1)

@app.command()
def logout():
    """Log out and clear stored credentials."""
    clear_tokens()
    console.print("[green]Logged out successfully[/green]")

@app.command()
def status():
    """Check authentication status."""
    from atlas_cli.storage.credentials import get_access_token

    if get_access_token():
        console.print("[green]Authenticated[/green]")
    else:
        console.print("[yellow]Not logged in[/yellow]")
        console.print("Run [bold]atlas auth login[/bold] to authenticate")
```

### Sync Command
```python
# commands/sync.py
import typer
from rich.console import Console
from rich.panel import Panel
from pathlib import Path

from atlas_cli.api.client import create_client
from atlas_cli.storage.files import atomic_write, get_config_path

console = Console()

@typer.command()
def sync(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be synced"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite even if local is newer"),
):
    """Sync configuration from Atlas to local ~/.claude/CLAUDE.md"""
    config_path = get_config_path()

    with console.status("Fetching configuration..."):
        try:
            with create_client() as client:
                response = client.get("/configuration/me")
                response.raise_for_status()

            data = response.json()
            remote_content = data["content"]
            remote_sha = data["commit_sha"]

        except Exception as e:
            console.print(f"[red]Failed to fetch configuration: {e}[/red]")
            raise typer.Exit(1)

    # Check if already synced
    if config_path.exists():
        local_content = config_path.read_text(encoding="utf-8")
        if local_content == remote_content:
            console.print("[green]Already up to date[/green]")
            return

    if dry_run:
        console.print(Panel(
            f"Would write {len(remote_content)} bytes to {config_path}",
            title="Dry Run",
        ))
        return

    # Atomic write
    with console.status("Writing configuration..."):
        atomic_write(config_path, remote_content)

    console.print(f"[green]Synced configuration to {config_path}[/green]")
    console.print(f"[dim]Commit: {remote_sha}[/dim]")
```

### Doctor Command
```python
# commands/doctor.py
import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path

console = Console()

@typer.command()
def doctor():
    """Check CLI configuration and connectivity."""
    table = Table(title="Atlas CLI Health Check")
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Details")

    # Check credentials
    from atlas_cli.storage.credentials import get_access_token
    token = get_access_token()
    if token:
        table.add_row("Authentication", "[green]OK[/green]", "Token stored")
    else:
        table.add_row("Authentication", "[red]FAIL[/red]", "Not logged in")

    # Check config directory
    config_dir = Path.home() / ".claude"
    if config_dir.exists():
        table.add_row("Config Directory", "[green]OK[/green]", str(config_dir))
    else:
        table.add_row("Config Directory", "[yellow]MISSING[/yellow]", "Will be created on sync")

    # Check connectivity
    import httpx
    try:
        response = httpx.get(
            "https://api.atlas.example.com/health",
            timeout=5.0,
        )
        if response.status_code == 200:
            table.add_row("API Connectivity", "[green]OK[/green]", "Connected")
        else:
            table.add_row("API Connectivity", "[yellow]DEGRADED[/yellow]", f"Status {response.status_code}")
    except httpx.RequestError as e:
        table.add_row("API Connectivity", "[red]FAIL[/red]", str(e))

    console.print(table)
```

### pyproject.toml for CLI Package
```toml
# cli/pyproject.toml
[project]
name = "atlas-cli"
version = "0.1.0"
description = "CLI tool to sync Claude configuration from Atlas platform"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "typer>=0.9.0",
    "httpx>=0.27.0",
    "keyring>=25.0.0",
    "rich>=14.0.0",
]

[project.scripts]
atlas = "atlas_cli.main:main"

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-httpx>=0.30.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/atlas_cli"]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| argparse | Typer with type hints | 2020+ | Much less boilerplate, auto-completion |
| requests | httpx | 2020+ | Async support, HTTP/2, better API |
| atomicwrites library | stdlib tempfile + os.replace | 2022 | Library deprecated, stdlib sufficient |
| Manual credential files | keyring | Always preferred | OS-native security |
| print() for output | Rich | 2020+ | Progress bars, tables, colors |

**Deprecated/outdated:**
- `atomicwrites`: Archived 2022, use `tempfile` + `os.replace()` instead
- `argparse`: Works but verbose - Typer preferred for new projects
- `requests` without session: httpx.Client provides connection pooling

## Open Questions

Things that couldn't be fully resolved:

1. **Backend API Base URL Configuration**
   - What we know: CLI needs to know where backend lives
   - What's unclear: Should be configurable or hardcoded for production?
   - Recommendation: Use environment variable `ATLAS_API_URL` with sensible default

2. **Refresh Token Cookie Handling**
   - What we know: Backend sets refresh_token as HttpOnly cookie
   - What's unclear: httpx doesn't persist cookies by default
   - Recommendation: Extract from response.cookies and store in keyring alongside access token

3. **CI/Server Keyring Fallback**
   - What we know: Headless Linux may not have keyring backend
   - What's unclear: What's the best fallback mechanism?
   - Recommendation: Detect and offer `--token-file` flag, document for CI usage

## Sources

### Primary (HIGH confidence)
- [Typer Official Docs](https://typer.tiangolo.com/) - CLI framework patterns
- [HTTPX Official Docs](https://www.python-httpx.org/) - Client, authentication, async
- [Keyring Official Docs](https://keyring.readthedocs.io/en/stable/) - Credential storage API
- [Rich Official Docs](https://rich.readthedocs.io/en/stable/) - Console output
- [Python tempfile Docs](https://docs.python.org/3/library/tempfile.html) - Atomic write pattern
- [Python pathlib Docs](https://docs.python.org/3/library/pathlib.html) - Cross-platform paths
- [uv Projects Guide](https://docs.astral.sh/uv/guides/projects/) - CLI entry points

### Secondary (MEDIUM confidence)
- [atomicwrites GitHub](https://github.com/untitaker/python-atomicwrites) - Deprecation notice, stdlib recommendation
- [HTTPX Advanced Auth](https://www.python-httpx.org/advanced/authentication/) - Custom auth flow

### Tertiary (LOW confidence)
- [WebSearch: CLI best practices](https://medium.com/@connect.hashblock/7-typer-cli-patterns-that-feel-like-real-tools-ecbe72720828) - Community patterns
- [WebSearch: Python monorepo uv](https://medium.com/@life-is-short-so-enjoy-it/python-monorepo-with-uv-f4ced6f1f425) - Workspace structure

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official docs consulted for all libraries
- Architecture: HIGH - Patterns from official documentation
- Pitfalls: MEDIUM - Mix of official docs and community experience

**Research date:** 2026-01-25
**Valid until:** ~60 days (stable ecosystem, libraries mature)
