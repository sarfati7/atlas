"""HTTP client factory for Atlas API communication."""

import httpx

from atlas_cli import __version__
from atlas_cli.api.auth import TokenAuth
from atlas_cli.config import config


def create_client() -> httpx.Client:
    """Create an authenticated httpx client for API requests.

    The client includes TokenAuth which automatically handles
    Bearer token authentication and token refresh on 401 responses.

    Returns:
        Configured httpx.Client with authentication.
    """
    return httpx.Client(
        base_url=config.api_base_url,
        auth=TokenAuth(),
        headers={"User-Agent": f"atlas-cli/{__version__}"},
        timeout=config.timeout,
    )


def create_unauthenticated_client() -> httpx.Client:
    """Create an unauthenticated httpx client.

    Used for endpoints that don't require authentication,
    such as the login endpoint.

    Returns:
        Configured httpx.Client without authentication.
    """
    return httpx.Client(
        base_url=config.api_base_url,
        headers={"User-Agent": f"atlas-cli/{__version__}"},
        timeout=config.timeout,
    )
