"""Tests for storage modules."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from atlas_cli.storage.files import atomic_write, get_claude_dir, get_config_path, read_config
from atlas_cli.storage.credentials import (
    get_access_token,
    is_authenticated,
    _check_keyring_available,
)


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


class TestCredentials:
    """Tests for credential storage."""

    def test_get_access_token_returns_env_var(self) -> None:
        """get_access_token returns ATLAS_ACCESS_TOKEN env var when set."""
        with patch.dict(os.environ, {"ATLAS_ACCESS_TOKEN": "test-token-from-env"}):
            result = get_access_token()
            assert result == "test-token-from-env"

    def test_get_access_token_env_var_takes_precedence(self) -> None:
        """ATLAS_ACCESS_TOKEN takes precedence over keyring."""
        with patch.dict(os.environ, {"ATLAS_ACCESS_TOKEN": "env-token"}):
            with patch("keyring.get_password", return_value="keyring-token"):
                result = get_access_token()
                assert result == "env-token"

    def test_get_access_token_falls_back_to_keyring(self) -> None:
        """get_access_token falls back to keyring when no env var."""
        with patch.dict(os.environ, {}, clear=True):
            # Ensure ATLAS_ACCESS_TOKEN is not set
            os.environ.pop("ATLAS_ACCESS_TOKEN", None)
            with patch("atlas_cli.storage.credentials.keyring.get_password", return_value="keyring-token"):
                result = get_access_token()
                assert result == "keyring-token"

    def test_get_access_token_returns_none_on_keyring_error(self) -> None:
        """get_access_token returns None when keyring fails."""
        from keyring.errors import KeyringError

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ATLAS_ACCESS_TOKEN", None)
            with patch("atlas_cli.storage.credentials.keyring.get_password", side_effect=KeyringError("No backend")):
                result = get_access_token()
                assert result is None

    def test_is_authenticated_with_env_var(self) -> None:
        """is_authenticated returns True when env var is set."""
        with patch.dict(os.environ, {"ATLAS_ACCESS_TOKEN": "test-token"}):
            assert is_authenticated() is True

    def test_is_authenticated_without_credentials(self) -> None:
        """is_authenticated returns False when no credentials."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ATLAS_ACCESS_TOKEN", None)
            with patch("atlas_cli.storage.credentials.keyring.get_password", return_value=None):
                assert is_authenticated() is False

    def test_check_keyring_available_returns_true_for_good_backend(self) -> None:
        """_check_keyring_available returns True for working backend."""
        mock_backend = MagicMock()
        type(mock_backend).__name__ = "macOS"
        with patch("atlas_cli.storage.credentials.keyring.get_keyring", return_value=mock_backend):
            assert _check_keyring_available() is True

    def test_check_keyring_available_returns_false_for_fail_backend(self) -> None:
        """_check_keyring_available returns False for Fail backend."""
        mock_backend = MagicMock()
        type(mock_backend).__name__ = "FailKeyring"
        with patch("atlas_cli.storage.credentials.keyring.get_keyring", return_value=mock_backend):
            assert _check_keyring_available() is False

    def test_check_keyring_available_returns_false_for_null_backend(self) -> None:
        """_check_keyring_available returns False for Null backend."""
        mock_backend = MagicMock()
        type(mock_backend).__name__ = "NullKeyring"
        with patch("atlas_cli.storage.credentials.keyring.get_keyring", return_value=mock_backend):
            assert _check_keyring_available() is False
