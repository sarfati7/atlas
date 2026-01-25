"""Keyring wrapper for secure credential storage.

Uses the OS keychain (macOS Keychain, Windows Credential Manager,
Linux Secret Service) for secure storage of authentication tokens.
Falls back to ATLAS_ACCESS_TOKEN environment variable for headless systems.
"""

import os

import keyring
from keyring.errors import KeyringError, PasswordDeleteError

SERVICE_NAME = "atlas-cli"


def _check_keyring_available() -> bool:
    """Check if a working keyring backend is available.

    Returns:
        True if a usable keyring backend exists, False otherwise.
    """
    try:
        backend = keyring.get_keyring()
        backend_name = type(backend).__name__
        # These backends don't actually store credentials
        return "Fail" not in backend_name and "Null" not in backend_name
    except Exception:
        return False


def save_tokens(access_token: str, refresh_token: str) -> None:
    """Save authentication tokens to the OS keychain.

    Args:
        access_token: The JWT access token.
        refresh_token: The refresh token for obtaining new access tokens.

    Raises:
        RuntimeError: If keyring fails (e.g., on headless systems).
    """
    try:
        keyring.set_password(SERVICE_NAME, "access_token", access_token)
        keyring.set_password(SERVICE_NAME, "refresh_token", refresh_token)
    except KeyringError as e:
        raise RuntimeError(
            f"Failed to store credentials in keyring: {e}\n"
            "If you're on a headless system, consider using ATLAS_ACCESS_TOKEN environment variable."
        ) from e


def get_access_token() -> str | None:
    """Retrieve access token from keychain or environment.

    Environment variable ATLAS_ACCESS_TOKEN takes precedence over keychain.
    This allows CI/headless systems to authenticate without keyring.

    Returns:
        The access token if present, None otherwise.
    """
    # Environment variable takes precedence (for CI/headless systems)
    env_token = os.environ.get("ATLAS_ACCESS_TOKEN")
    if env_token:
        return env_token

    try:
        return keyring.get_password(SERVICE_NAME, "access_token")
    except KeyringError:
        return None


def get_refresh_token() -> str | None:
    """Retrieve the refresh token from the OS keychain.

    Returns:
        The refresh token if present, None otherwise.
    """
    try:
        return keyring.get_password(SERVICE_NAME, "refresh_token")
    except KeyringError:
        return None


def clear_tokens() -> None:
    """Remove all tokens from the OS keychain.

    Safe to call even if no tokens exist or keyring fails.
    """
    try:
        keyring.delete_password(SERVICE_NAME, "access_token")
    except (PasswordDeleteError, KeyringError):
        pass

    try:
        keyring.delete_password(SERVICE_NAME, "refresh_token")
    except (PasswordDeleteError, KeyringError):
        pass


def is_authenticated() -> bool:
    """Check if the user is authenticated.

    Returns:
        True if an access token exists (from keychain or env), False otherwise.
    """
    return get_access_token() is not None
