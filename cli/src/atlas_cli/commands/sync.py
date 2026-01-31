"""Sync command - fetch configuration from Atlas and write locally."""

import typer
from rich.panel import Panel

from atlas_cli.api.client import create_client
from atlas_cli.console import console, error, info, success
from atlas_cli.storage.credentials import is_authenticated
from atlas_cli.storage.files import atomic_write, get_config_path, read_config


def sync(
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Show what would be synced without writing"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite even if local content differs"
    ),
) -> None:
    """Sync configuration from Atlas to local ~/.claude/CLAUDE.md."""
    # Check authentication first
    if not is_authenticated():
        error("Not logged in. Run 'axon auth login' first.")
        raise typer.Exit(1)

    config_path = get_config_path()

    # Fetch remote configuration
    with console.status("Fetching configuration from Atlas..."):
        try:
            with create_client() as client:
                response = client.get("/configuration/me")
                response.raise_for_status()

            data = response.json()
            remote_content = data.get("content", "")
            remote_sha = data.get("commit_sha", "unknown")

        except Exception as e:
            error(f"Failed to fetch configuration: {e}")
            raise typer.Exit(1)

    # Check if empty configuration
    if not remote_content.strip():
        info("No configuration found on Atlas. Nothing to sync.")
        info("Create your configuration at the Atlas web interface first.")
        return

    # Check if already synced
    local_content = read_config()
    if local_content is not None and local_content == remote_content:
        success("Already up to date.")
        info(f"Commit: {remote_sha[:7]}")
        return

    # Show diff summary
    if local_content is not None and not force:
        console.print(f"\n[yellow]Local file will be updated:[/yellow] {config_path}")
        console.print(f"[dim]Remote commit: {remote_sha[:7]}[/dim]")

    # Dry run - just show what would happen
    if dry_run:
        console.print(
            Panel(
                f"Would write {len(remote_content)} bytes to {config_path}\n"
                f"Commit: {remote_sha[:7]}",
                title="[cyan]Dry Run[/cyan]",
                border_style="cyan",
            )
        )
        return

    # Perform atomic write
    with console.status("Writing configuration..."):
        try:
            atomic_write(config_path, remote_content)
        except Exception as e:
            error(f"Failed to write configuration: {e}")
            raise typer.Exit(1)

    success(f"Synced configuration to {config_path}")
    info(f"Commit: {remote_sha[:7]}")
