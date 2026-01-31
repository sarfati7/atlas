"""Pull command - download configuration and catalog items from Atlas."""

from pathlib import Path
from typing import Optional

import typer
from rich.panel import Panel
from rich.table import Table

from atlas_cli.api.client import create_client
from atlas_cli.console import console, error, info, success, warning
from atlas_cli.storage.credentials import is_authenticated
from atlas_cli.storage.files import atomic_write, get_claude_dir, get_config_path, read_config


def _build_skill_content(name: str, description: str, tags: list[str], content: str) -> str:
    """Build SKILL.md content with YAML frontmatter."""
    tags_str = ", ".join(tags) if tags else ""
    frontmatter = f"""---
name: {name}
description: {description}
tags: [{tags_str}]
---

"""
    return frontmatter + content


def pull(
    config_only: bool = typer.Option(
        False, "--config-only", "-c", help="Only pull CLAUDE.md configuration"
    ),
    item_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Only pull items of this type (skill, mcp, tool)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be pulled without writing"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite local files even if they differ"
    ),
) -> None:
    """Pull configuration and catalog items from Atlas.

    Downloads your CLAUDE.md and all your skills/MCPs/tools from Atlas
    to your local ~/.claude/ directory.
    """
    if not is_authenticated():
        error("Not logged in. Run 'axon auth login' first.")
        raise typer.Exit(1)

    config_path = get_config_path()
    claude_dir = get_claude_dir()

    pulled_config = False
    pulled_items = 0
    skipped_items = 0

    # Pull CLAUDE.md configuration
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

    # Handle CLAUDE.md
    if remote_content.strip():
        local_content = read_config()

        if local_content is not None and local_content == remote_content:
            info(f"CLAUDE.md: already up to date (commit: {remote_sha[:7]})")
        else:
            if dry_run:
                console.print(f"[cyan]Would update:[/cyan] {config_path}")
            else:
                atomic_write(config_path, remote_content)
                success(f"CLAUDE.md: synced (commit: {remote_sha[:7]})")
                pulled_config = True
    else:
        info("CLAUDE.md: no configuration found on Atlas")

    # If config-only, stop here
    if config_only:
        return

    # Pull catalog items
    with console.status("Fetching catalog items from Atlas..."):
        try:
            with create_client() as client:
                # Get user's catalog items (filter by user scope)
                response = client.get("/catalog", params={"size": 100})
                response.raise_for_status()

            data = response.json()
            items = data.get("items", [])

            # Filter to only user-scoped items (owned by current user)
            user_items = [i for i in items if i.get("scope") == "user"]

            # Filter by type if specified
            if item_type:
                user_items = [i for i in user_items if i.get("type") == item_type]

        except Exception as e:
            error(f"Failed to fetch catalog: {e}")
            raise typer.Exit(1)

    if not user_items:
        info("No catalog items found to pull.")
        return

    # Show items to pull
    table = Table(title="Items to Pull")
    table.add_column("Type", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")

    for item in user_items:
        table.add_row(
            item["type"],
            item["name"],
            item["description"][:50] + "..." if len(item.get("description", "")) > 50 else item.get("description", ""),
        )

    console.print(table)

    if dry_run:
        info(f"\n[dim]Dry run: would pull {len(user_items)} item(s)[/dim]")
        return

    # Download each item
    with console.status("Downloading items..."):
        with create_client() as client:
            for item in user_items:
                item_id = item["id"]
                item_name = item["name"]
                item_type_str = item["type"]

                try:
                    # Get raw content
                    response = client.get(f"/catalog/items/{item_id}/raw")
                    response.raise_for_status()

                    raw_data = response.json()

                    # Determine local path
                    type_dir = {
                        "skill": "skills",
                        "mcp": "mcps",
                        "tool": "tools",
                    }.get(item_type_str, f"{item_type_str}s")

                    item_dir = claude_dir / type_dir / item_name
                    skill_file = item_dir / "SKILL.md"

                    # Build content with frontmatter
                    full_content = _build_skill_content(
                        name=raw_data["name"],
                        description=raw_data["description"],
                        tags=raw_data["tags"],
                        content=raw_data["content"],
                    )

                    # Check if local file exists and differs
                    if skill_file.exists() and not force:
                        local_content = skill_file.read_text(encoding="utf-8")
                        if local_content == full_content:
                            info(f"  {item_name}: already up to date")
                            skipped_items += 1
                            continue

                    # Write file
                    atomic_write(skill_file, full_content)
                    pulled_items += 1

                except Exception as e:
                    warning(f"  {item_name}: failed to download ({e})")

    # Summary
    if pulled_config or pulled_items > 0:
        success(f"Pulled: CLAUDE.md + {pulled_items} item(s)")
    if skipped_items > 0:
        info(f"Skipped {skipped_items} item(s) (already up to date)")
