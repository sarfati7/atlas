"""Atomic file write utilities for safe configuration syncing.

Uses temp file + rename pattern to ensure no partial writes occur,
even if the process is interrupted mid-write.
"""

import os
import tempfile
from pathlib import Path


def get_claude_dir() -> Path:
    """Get the Claude configuration directory path.

    Returns:
        Path to ~/.claude (cross-platform).
    """
    return Path.home() / ".claude"


def get_config_path() -> Path:
    """Get the Claude configuration file path.

    Returns:
        Path to ~/.claude/CLAUDE.md.
    """
    return get_claude_dir() / "CLAUDE.md"


def atomic_write(path: Path, content: str) -> None:
    """Write content to a file atomically.

    Uses a temp file + rename pattern to ensure the file is either
    fully written or not modified at all. This prevents partial
    writes if the process is interrupted.

    Args:
        path: The destination file path.
        content: The content to write.

    Raises:
        OSError: If the write or rename fails.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=".tmp_",
        suffix=path.suffix or ".md",
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def read_config() -> str | None:
    """Read the Claude configuration file.

    Returns:
        The configuration content if the file exists, None otherwise.
    """
    config_path = get_config_path()
    if config_path.exists():
        return config_path.read_text(encoding="utf-8")
    return None
