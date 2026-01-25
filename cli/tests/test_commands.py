"""Tests for CLI commands."""

from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from atlas_cli.main import app

runner = CliRunner()


class TestAuthCommands:
    """Tests for auth commands."""

    def test_auth_status_not_logged_in(self) -> None:
        """auth status shows not logged in when no token."""
        with patch("atlas_cli.commands.auth.is_authenticated", return_value=False):
            result = runner.invoke(app, ["auth", "status"])

            assert result.exit_code == 0
            assert "Not logged in" in result.output

    def test_auth_status_logged_in(self) -> None:
        """auth status shows authenticated when token exists."""
        with patch("atlas_cli.commands.auth.is_authenticated", return_value=True):
            result = runner.invoke(app, ["auth", "status"])

            assert result.exit_code == 0
            assert "Authenticated" in result.output

    def test_auth_logout_clears_tokens(self) -> None:
        """auth logout calls clear_tokens."""
        with patch("atlas_cli.commands.auth.clear_tokens") as mock_clear:
            result = runner.invoke(app, ["auth", "logout"])

            assert result.exit_code == 0
            mock_clear.assert_called_once()


class TestSyncCommand:
    """Tests for sync command."""

    def test_sync_requires_auth(self) -> None:
        """sync shows error when not authenticated."""
        with patch("atlas_cli.commands.sync.is_authenticated", return_value=False):
            result = runner.invoke(app, ["sync"])

            assert result.exit_code == 1
            assert "Not logged in" in result.output

    def test_sync_dry_run(self) -> None:
        """sync --dry-run shows preview without writing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": "# Test config",
            "commit_sha": "abc1234567890"
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response

        with patch("atlas_cli.commands.sync.is_authenticated", return_value=True):
            with patch("atlas_cli.commands.sync.create_client", return_value=mock_client):
                with patch("atlas_cli.commands.sync.read_config", return_value=None):
                    result = runner.invoke(app, ["sync", "--dry-run"])

                    assert result.exit_code == 0
                    assert "Dry Run" in result.output


class TestDoctorCommand:
    """Tests for doctor command."""

    def test_doctor_shows_checks(self) -> None:
        """doctor shows health check table."""
        mock_dir = MagicMock()
        mock_dir.exists.return_value = True

        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.stat.return_value = MagicMock(st_size=100)

        with patch("atlas_cli.commands.doctor.is_authenticated", return_value=True):
            with patch("atlas_cli.commands.doctor.get_claude_dir", return_value=mock_dir):
                with patch("atlas_cli.commands.doctor.get_config_path", return_value=mock_path):
                    with patch("httpx.get") as mock_get:
                        mock_get.return_value = MagicMock(status_code=200)
                        with patch("keyring.get_keyring") as mock_keyring:
                            mock_backend = MagicMock()
                            type(mock_backend).__name__ = "macOS"
                            mock_keyring.return_value = mock_backend

                            result = runner.invoke(app, ["doctor"])

                            assert "Health Check" in result.output


class TestStatusCommand:
    """Tests for status command."""

    def test_status_shows_local_missing(self) -> None:
        """status shows when local config is missing."""
        with patch("atlas_cli.commands.status.read_config", return_value=None):
            with patch("atlas_cli.commands.status.is_authenticated", return_value=False):
                result = runner.invoke(app, ["status"])

                assert result.exit_code == 0
                assert "not found" in result.output

    def test_status_shows_local_exists(self) -> None:
        """status shows local config info when exists."""
        with patch("atlas_cli.commands.status.read_config", return_value="# Test config"):
            with patch("atlas_cli.commands.status.is_authenticated", return_value=False):
                result = runner.invoke(app, ["status"])

                assert result.exit_code == 0
                assert "bytes" in result.output


class TestHelpOutput:
    """Tests for help output."""

    def test_main_help(self) -> None:
        """Main help shows available commands."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "auth" in result.output
        assert "sync" in result.output
        assert "doctor" in result.output
        assert "status" in result.output

    def test_version(self) -> None:
        """--version shows version."""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "atlas-cli" in result.output
