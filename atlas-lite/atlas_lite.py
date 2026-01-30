#!/usr/bin/env python3
"""Atlas Lite: Git-only sync for Claude configuration.

No backend required. Just syncs from a Git repo to ~/.claude/

Usage:
    atlas-lite sync                    # Sync everything
    atlas-lite sync --dry-run          # Preview changes
    atlas-lite status                  # Show sync status
    atlas-lite init <repo-url>         # Initialize with repo URL
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CONFIG_FILE = Path.home() / ".atlas-lite.json"
CLAUDE_DIR = Path.home() / ".claude"
CACHE_DIR = Path.home() / ".cache" / "atlas-lite"


def load_config() -> dict:
    """Load configuration from ~/.atlas-lite.json"""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(config: dict) -> None:
    """Save configuration to ~/.atlas-lite.json"""
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def run_git(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except FileNotFoundError:
        return False, "Git is not installed"


def file_hash(path: Path) -> str:
    """Get MD5 hash of a file."""
    if not path.exists():
        return ""
    return hashlib.md5(path.read_bytes()).hexdigest()


def init_repo(repo_url: str) -> None:
    """Initialize atlas-lite with a repository URL."""
    config = load_config()
    config["repo_url"] = repo_url
    save_config(config)
    print(f"Configured repository: {repo_url}")
    print(f"Config saved to: {CONFIG_FILE}")
    print("\nRun 'atlas-lite sync' to sync files.")


def sync(dry_run: bool = False) -> None:
    """Sync from Git repo to ~/.claude/"""
    config = load_config()
    repo_url = config.get("repo_url")

    if not repo_url:
        print("No repository configured.")
        print("Run: atlas-lite init <repo-url>")
        sys.exit(1)

    # Ensure cache directory exists
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    repo_dir = CACHE_DIR / "repo"

    # Clone or pull
    if repo_dir.exists():
        print(f"Pulling latest from {repo_url}...")
        success, output = run_git(["pull", "--ff-only"], cwd=repo_dir)
        if not success:
            print(f"Pull failed: {output}")
            print("Trying fresh clone...")
            shutil.rmtree(repo_dir)
            success, output = run_git(["clone", repo_url, str(repo_dir)])
            if not success:
                print(f"Clone failed: {output}")
                sys.exit(1)
    else:
        print(f"Cloning {repo_url}...")
        success, output = run_git(["clone", repo_url, str(repo_dir)])
        if not success:
            print(f"Clone failed: {output}")
            sys.exit(1)

    # Get current commit
    _, commit = run_git(["rev-parse", "--short", "HEAD"], cwd=repo_dir)
    commit = commit.strip()
    print(f"At commit: {commit}")

    # Ensure claude directory exists
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)

    # Sync items
    changes = []

    # Sync CLAUDE.md if exists
    claude_md = repo_dir / "CLAUDE.md"
    if claude_md.exists():
        dest = CLAUDE_DIR / "CLAUDE.md"
        if file_hash(claude_md) != file_hash(dest):
            changes.append(("update" if dest.exists() else "create", "CLAUDE.md"))
            if not dry_run:
                shutil.copy2(claude_md, dest)

    # Sync directories (skills, commands/mcps, tools)
    sync_dirs = [
        ("skills", "skills"),
        ("mcps", "commands"),  # mcps in repo -> commands locally
        ("tools", "tools"),
    ]

    for repo_name, local_name in sync_dirs:
        repo_path = repo_dir / repo_name
        local_path = CLAUDE_DIR / local_name

        if not repo_path.exists():
            continue

        local_path.mkdir(parents=True, exist_ok=True)

        # Sync each item directory
        for item_dir in repo_path.iterdir():
            if not item_dir.is_dir():
                continue

            item_name = item_dir.name
            dest_dir = local_path / item_name

            # Find the main file (SKILL.md, README.md, or config.yaml)
            main_file = None
            for candidate in ["SKILL.md", "README.md", "config.yaml"]:
                if (item_dir / candidate).exists():
                    main_file = item_dir / candidate
                    break

            if not main_file:
                continue

            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / main_file.name

            if file_hash(main_file) != file_hash(dest_file):
                action = "update" if dest_file.exists() else "create"
                changes.append((action, f"{local_name}/{item_name}/{main_file.name}"))
                if not dry_run:
                    shutil.copy2(main_file, dest_file)

            # Also copy config.yaml if separate from main file
            config_yaml = item_dir / "config.yaml"
            if config_yaml.exists() and config_yaml != main_file:
                dest_config = dest_dir / "config.yaml"
                if file_hash(config_yaml) != file_hash(dest_config):
                    if not dry_run:
                        shutil.copy2(config_yaml, dest_config)

    # Report results
    if dry_run:
        print("\nDry run - no changes made")

    if changes:
        print(f"\n{'Would sync' if dry_run else 'Synced'} {len(changes)} file(s):")
        for action, path in changes:
            symbol = "+" if action == "create" else "~"
            print(f"  {symbol} {path}")
    else:
        print("\nAlready up to date.")

    if not dry_run:
        config["last_sync"] = commit
        save_config(config)


def status() -> None:
    """Show sync status."""
    config = load_config()
    repo_url = config.get("repo_url")
    last_sync = config.get("last_sync")

    print("Atlas Lite Status")
    print("-" * 40)
    print(f"Config file: {CONFIG_FILE}")
    print(f"Claude dir:  {CLAUDE_DIR}")
    print(f"Cache dir:   {CACHE_DIR}")
    print()

    if not repo_url:
        print("Repository: Not configured")
        print("\nRun: atlas-lite init <repo-url>")
        return

    print(f"Repository: {repo_url}")
    print(f"Last sync:  {last_sync or 'Never'}")

    # Check if repo has updates
    repo_dir = CACHE_DIR / "repo"
    if repo_dir.exists():
        run_git(["fetch"], cwd=repo_dir)
        _, local = run_git(["rev-parse", "HEAD"], cwd=repo_dir)
        _, remote = run_git(["rev-parse", "origin/HEAD"], cwd=repo_dir)

        if local.strip() != remote.strip():
            print("\nUpdates available! Run: atlas-lite sync")

    # Show what's in claude dir
    print(f"\nLocal files in {CLAUDE_DIR}:")
    if CLAUDE_DIR.exists():
        for item in sorted(CLAUDE_DIR.iterdir()):
            if item.name.startswith("."):
                continue
            if item.is_file():
                print(f"  {item.name}")
            elif item.is_dir():
                count = len(list(item.iterdir()))
                print(f"  {item.name}/ ({count} items)")
    else:
        print("  (directory doesn't exist)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Atlas Lite: Git-only sync for Claude configuration"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize with repo URL")
    init_parser.add_argument("repo_url", help="Git repository URL")

    # sync command
    sync_parser = subparsers.add_parser("sync", help="Sync from Git to ~/.claude/")
    sync_parser.add_argument(
        "--dry-run", "-d", action="store_true", help="Preview changes without syncing"
    )

    # status command
    subparsers.add_parser("status", help="Show sync status")

    args = parser.parse_args()

    if args.command == "init":
        init_repo(args.repo_url)
    elif args.command == "sync":
        sync(dry_run=args.dry_run)
    elif args.command == "status":
        status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
