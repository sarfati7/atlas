"""Push command - upload local skills/MCPs/tools to Atlas."""

import re
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.table import Table

from atlas_cli.api.client import create_client
from atlas_cli.console import console, error, info, success, warning
from atlas_cli.storage.credentials import is_authenticated
from atlas_cli.storage.files import get_claude_dir


def _parse_skill_file(skill_path: Path) -> dict | None:
    """Parse a SKILL.md file and extract metadata and content.

    Returns dict with name, description, tags, content or None if invalid.
    """
    if not skill_path.exists():
        return None

    content = skill_path.read_text(encoding="utf-8")

    # Check for YAML frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return {
                    "name": frontmatter.get("name", skill_path.parent.name),
                    "description": frontmatter.get("description", ""),
                    "tags": frontmatter.get("tags", []),
                    "content": body,
                }
            except yaml.YAMLError:
                pass

    # No frontmatter - use directory name and full content
    return {
        "name": skill_path.parent.name,
        "description": "",
        "tags": [],
        "content": content,
    }


def _scan_local_items(item_type: str) -> list[dict]:
    """Scan local directory for items of given type.

    Args:
        item_type: 'skill', 'mcp', or 'tool'

    Returns list of parsed items with path info.
    """
    claude_dir = get_claude_dir()

    # Map type to directory name
    type_dirs = {
        "skill": "skills",
        "mcp": "mcps",
        "tool": "tools",
    }

    items_dir = claude_dir / type_dirs.get(item_type, f"{item_type}s")
    if not items_dir.exists():
        return []

    items = []
    for item_dir in items_dir.iterdir():
        if not item_dir.is_dir():
            continue

        # Look for SKILL.md, MCP.md, TOOL.md, or README.md
        skill_file = item_dir / "SKILL.md"
        if not skill_file.exists():
            skill_file = item_dir / f"{item_type.upper()}.md"
        if not skill_file.exists():
            skill_file = item_dir / "README.md"

        if skill_file.exists():
            parsed = _parse_skill_file(skill_file)
            if parsed:
                parsed["path"] = item_dir
                parsed["type"] = item_type
                items.append(parsed)

    return items


def push(
    item_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Only push items of this type (skill, mcp, tool)"
    ),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Only push item with this name"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be pushed without uploading"
    ),
) -> None:
    """Push local skills, MCPs, and tools to Atlas.

    Scans ~/.claude/skills/, ~/.claude/mcps/, ~/.claude/tools/ and uploads
    each item to your Atlas catalog.
    """
    if not is_authenticated():
        error("Not logged in. Run 'axon auth login' first.")
        raise typer.Exit(1)

    # Determine which types to scan
    types_to_scan = ["skill", "mcp", "tool"]
    if item_type:
        if item_type not in types_to_scan:
            error(f"Invalid type '{item_type}'. Must be: skill, mcp, or tool")
            raise typer.Exit(1)
        types_to_scan = [item_type]

    # Scan for items
    all_items = []
    for t in types_to_scan:
        items = _scan_local_items(t)
        all_items.extend(items)

    # Filter by name if specified
    if name:
        all_items = [i for i in all_items if i["name"] == name]

    if not all_items:
        info("No items found to push.")
        if name:
            info(f"No item named '{name}' found in ~/.claude/")
        return

    # Show what will be pushed
    table = Table(title="Items to Push")
    table.add_column("Type", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")
    table.add_column("Tags")

    for item in all_items:
        table.add_row(
            item["type"],
            item["name"],
            item["description"][:50] + "..." if len(item["description"]) > 50 else item["description"],
            ", ".join(item["tags"]) if item["tags"] else "-",
        )

    console.print(table)

    if dry_run:
        info(f"\n[dim]Dry run: would push {len(all_items)} item(s)[/dim]")
        return

    # Push each item
    pushed = 0
    failed = 0

    with console.status("Pushing items to Atlas..."):
        with create_client() as client:
            for item in all_items:
                try:
                    response = client.post(
                        "/catalog/items",
                        json={
                            "type": item["type"],
                            "name": item["name"],
                            "description": item["description"],
                            "tags": item["tags"],
                            "content": item["content"],
                        },
                    )

                    if response.status_code == 201:
                        pushed += 1
                    elif response.status_code == 400:
                        # Item already exists - try update
                        data = response.json()
                        if "already exists" in data.get("detail", ""):
                            # Find item ID and update
                            warning(f"  {item['name']}: already exists, skipping")
                            failed += 1
                        else:
                            error(f"  {item['name']}: {data.get('detail', 'Bad request')}")
                            failed += 1
                    else:
                        response.raise_for_status()

                except Exception as e:
                    error(f"  {item['name']}: {e}")
                    failed += 1

    # Summary
    if pushed > 0:
        success(f"Pushed {pushed} item(s) to Atlas")
    if failed > 0:
        warning(f"{failed} item(s) failed or skipped")

    # Refresh catalog cache
    if pushed > 0:
        with console.status("Refreshing catalog..."):
            try:
                with create_client() as client:
                    client.post("/catalog/refresh")
            except Exception:
                pass
