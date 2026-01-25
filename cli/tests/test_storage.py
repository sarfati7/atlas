"""Tests for storage modules."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from atlas_cli.storage.files import atomic_write, get_claude_dir, get_config_path, read_config


class TestAtomicWrite:
    """Tests for atomic file write."""

    def test_atomic_write_creates_file(self, tmp_path: Path) -> None:
        """atomic_write creates file with correct content."""
        test_file = tmp_path / "test.md"
        content = "# Test Content\n\nHello, World!"

        atomic_write(test_file, content)

        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == content

    def test_atomic_write_creates_parent_dirs(self, tmp_path: Path) -> None:
        """atomic_write creates parent directories if needed."""
        test_file = tmp_path / "nested" / "dir" / "test.md"
        content = "Nested content"

        atomic_write(test_file, content)

        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == content

    def test_atomic_write_overwrites_existing(self, tmp_path: Path) -> None:
        """atomic_write overwrites existing file."""
        test_file = tmp_path / "test.md"
        test_file.write_text("old content")

        atomic_write(test_file, "new content")

        assert test_file.read_text(encoding="utf-8") == "new content"

    def test_atomic_write_no_partial_on_error(self, tmp_path: Path) -> None:
        """atomic_write leaves no partial file on write error."""
        test_file = tmp_path / "test.md"
        test_file.write_text("original")

        # Simulate write failure by making the content raise during write
        with patch("os.fdopen") as mock_fdopen:
            mock_file = MagicMock()
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=False)
            mock_file.write.side_effect = IOError("Simulated write failure")
            mock_fdopen.return_value = mock_file

            with pytest.raises(IOError):
                atomic_write(test_file, "new content that fails")

        # Original file should be unchanged
        assert test_file.read_text(encoding="utf-8") == "original"

    def test_atomic_write_handles_unicode(self, tmp_path: Path) -> None:
        """atomic_write handles unicode content correctly."""
        test_file = tmp_path / "test.md"
        content = "# Unicode Test\n\nJapanese: \u65e5\u672c\u8a9e emoji: special chars: \u00e4\u00f6\u00fc"

        atomic_write(test_file, content)

        assert test_file.read_text(encoding="utf-8") == content


class TestPaths:
    """Tests for path utilities."""

    def test_get_claude_dir_returns_path(self) -> None:
        """get_claude_dir returns Path object."""
        result = get_claude_dir()
        assert isinstance(result, Path)
        assert result.name == ".claude"

    def test_get_claude_dir_is_in_home(self) -> None:
        """get_claude_dir is under home directory."""
        result = get_claude_dir()
        assert result.parent == Path.home()

    def test_get_config_path_returns_claude_md(self) -> None:
        """get_config_path returns CLAUDE.md path."""
        result = get_config_path()
        assert result.name == "CLAUDE.md"
        assert result.parent == get_claude_dir()


class TestReadConfig:
    """Tests for read_config."""

    def test_read_config_returns_content(self, tmp_path: Path) -> None:
        """read_config returns file content when exists."""
        with patch("atlas_cli.storage.files.get_config_path") as mock_path:
            test_file = tmp_path / "CLAUDE.md"
            test_file.write_text("test content")
            mock_path.return_value = test_file

            result = read_config()

            assert result == "test content"

    def test_read_config_returns_none_when_missing(self, tmp_path: Path) -> None:
        """read_config returns None when file doesn't exist."""
        with patch("atlas_cli.storage.files.get_config_path") as mock_path:
            mock_path.return_value = tmp_path / "nonexistent.md"

            result = read_config()

            assert result is None
