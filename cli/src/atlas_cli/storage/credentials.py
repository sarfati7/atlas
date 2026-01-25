"""Keyring wrapper for secure credential storage.

Uses the OS keychain (macOS Keychain, Windows Credential Manager,
Linux Secret Service) for secure storage of authentication tokens.
"""

import keyring
from keyring.errors import PasswordDeleteError

SERVICE_NAME = "atlas-cli"


def save_tokens(access_token: str, refresh_token: str) -> None:
    """Save authentication tokens to the OS keychain.

    Args:
        access_token: The JWT access token.
        refresh_token: The refresh token for obtaining new access tokens.
    """
    keyring.set_password(SERVICE_NAME, "access_token", access_token)
    keyring.set_password(SERVICE_NAME, "refresh_token", refresh_token)


def get_access_token() -> str | None:
    """Retrieve the access token from the OS keychain.

    Returns:
        The access token if present, None otherwise.
    """
    return keyring.get_password(SERVICE_NAME, "access_token")


def get_refresh_token() -> str | None:
    """Retrieve the refresh token from the OS keychain.

    Returns:
        The refresh token if present, None otherwise.
    """
    return keyring.get_password(SERVICE_NAME, "refresh_token")


def clear_tokens() -> None:
    """Remove all tokens from the OS keychain.

    Safe to call even if no tokens exist.
    """
    try:
        keyring.delete_password(SERVICE_NAME, "access_token")
    except PasswordDeleteError:
        pass

    try:
        keyring.delete_password(SERVICE_NAME, "refresh_token")
    except PasswordDeleteError:
        pass


def is_authenticated() -> bool:
    """Check if the user is authenticated.

    Returns:
        True if an access token exists, False otherwise.
    """
    return get_access_token() is not None
