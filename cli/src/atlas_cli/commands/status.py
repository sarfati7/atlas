"""Status command - quick sync status check."""

from atlas_cli.api.client import create_client
from atlas_cli.console import console, info
from atlas_cli.storage.credentials import is_authenticated
from atlas_cli.storage.files import get_config_path, read_config


def status() -> None:
    """Show sync status - compare local config with remote."""
    config_path = get_config_path()

    # Check local config
    local_content = read_config()
    local_exists = local_content is not None

    console.print("[bold]Atlas Sync Status[/bold]\n")

    # Local status
    if local_exists:
        local_size = len(local_content) if local_content else 0
        console.print(f"[cyan]Local:[/cyan]  {config_path} ({local_size} bytes)")
    else:
        console.print(f"[cyan]Local:[/cyan]  {config_path} [yellow](not found)[/yellow]")

    # Check if authenticated for remote status
    if not is_authenticated():
        console.print("[cyan]Remote:[/cyan] [dim]Login required to check remote status[/dim]")
        info("\nRun 'axon auth login' to authenticate.")
        return

    # Fetch remote status
    try:
        with console.status("Checking remote..."):
            with create_client() as client:
                response = client.get("/configuration/me")
                response.raise_for_status()

            data = response.json()
            remote_content = data.get("content", "")
            remote_sha = data.get("commit_sha", "unknown")

        if remote_content:
            console.print(
                f"[cyan]Remote:[/cyan] {len(remote_content)} bytes (commit: {remote_sha[:7]})"
            )
        else:
            console.print("[cyan]Remote:[/cyan] [yellow](no configuration)[/yellow]")

        # Compare
        console.print()
        if not remote_content:
            console.print("[yellow]No remote configuration. Create one in Atlas web UI.[/yellow]")
        elif not local_exists:
            console.print("[yellow]Local config missing. Run 'axon sync' to download.[/yellow]")
        elif local_content == remote_content:
            console.print("[green]In sync[/green] - local matches remote")
        else:
            console.print("[yellow]Out of sync[/yellow] - local differs from remote")
            console.print("Run 'axon sync' to update local config")

    except Exception as e:
        console.print(f"[cyan]Remote:[/cyan] [red]Error: {e}[/red]")
