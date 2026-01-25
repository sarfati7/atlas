"""Doctor command - health check for Atlas CLI."""

import httpx
import typer
from rich.table import Table

from atlas_cli.config import config
from atlas_cli.console import console
from atlas_cli.storage.credentials import is_authenticated
from atlas_cli.storage.files import get_claude_dir, get_config_path


def doctor() -> None:
    """Check CLI configuration and connectivity."""
    table = Table(title="Atlas CLI Health Check")
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Details")

    all_ok = True

    # Check 1: Authentication
    if is_authenticated():
        table.add_row("Authentication", "[green]OK[/green]", "Token stored in keychain")
    else:
        table.add_row(
            "Authentication",
            "[red]FAIL[/red]",
            "Not logged in - run 'atlas auth login'",
        )
        all_ok = False

    # Check 2: Config directory
    config_dir = get_claude_dir()
    if config_dir.exists():
        table.add_row("Config Directory", "[green]OK[/green]", str(config_dir))
    else:
        table.add_row(
            "Config Directory",
            "[yellow]MISSING[/yellow]",
            f"{config_dir} - will be created on sync",
        )

    # Check 3: Config file
    config_path = get_config_path()
    if config_path.exists():
        size = config_path.stat().st_size
        table.add_row("Config File", "[green]OK[/green]", f"{config_path} ({size} bytes)")
    else:
        table.add_row(
            "Config File",
            "[yellow]MISSING[/yellow]",
            f"{config_path} - run 'atlas sync'",
        )

    # Check 4: API connectivity
    try:
        # Use unauthenticated request to health endpoint
        response = httpx.get(
            f"{config.api_base_url.rstrip('/api/v1')}/health",
            timeout=5.0,
        )
        if response.status_code == 200:
            table.add_row("API Connectivity", "[green]OK[/green]", config.api_base_url)
        else:
            table.add_row(
                "API Connectivity",
                "[yellow]DEGRADED[/yellow]",
                f"Status {response.status_code}",
            )
            all_ok = False
    except httpx.RequestError as e:
        table.add_row(
            "API Connectivity",
            "[red]FAIL[/red]",
            f"Cannot reach API: {type(e).__name__}",
        )
        all_ok = False

    # Check 5: Keyring backend
    try:
        import keyring

        backend = keyring.get_keyring()
        backend_name = type(backend).__name__
        if "Fail" in backend_name or "Null" in backend_name:
            table.add_row(
                "Keyring Backend",
                "[yellow]WARN[/yellow]",
                f"{backend_name} - credentials may not persist",
            )
        else:
            table.add_row("Keyring Backend", "[green]OK[/green]", backend_name)
    except Exception as e:
        table.add_row("Keyring Backend", "[red]FAIL[/red]", str(e))
        all_ok = False

    console.print(table)

    # Summary
    console.print()
    if all_ok:
        console.print("[green]All checks passed![/green]")
    else:
        console.print("[yellow]Some issues found. See above for details.[/yellow]")
        raise typer.Exit(1)
