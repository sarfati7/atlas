"""Custom httpx authentication with automatic token refresh."""

from typing import Generator

import httpx

from atlas_cli.config import config
from atlas_cli.storage.credentials import (
    get_access_token,
    get_refresh_token,
    save_tokens,
)


class TokenAuth(httpx.Auth):
    """httpx Auth that handles Bearer tokens with automatic refresh."""

    requires_response_body = True

    def __init__(self) -> None:
        """Load tokens from keyring."""
        self.access_token = get_access_token()
        self.refresh_token = get_refresh_token()

    def auth_flow(
        self,
        request: httpx.Request,
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """Handle authentication flow with automatic token refresh.

        If the access token is expired and we have a refresh token,
        automatically refreshes the access token and retries the request.
        """
        if self.access_token is None:
            yield request
            return

        request.headers["Authorization"] = f"Bearer {self.access_token}"
        response = yield request

        if response.status_code == 401 and self.refresh_token:
            refresh_request = httpx.Request(
                "POST",
                f"{config.api_base_url}/auth/refresh",
                headers={"Cookie": f"refresh_token={self.refresh_token}"},
            )
            refresh_response = yield refresh_request

            if refresh_response.status_code == 200:
                data = refresh_response.json()
                new_access_token = data["access_token"]

                new_refresh_token = self.refresh_token
                for cookie in refresh_response.headers.get_list("set-cookie"):
                    if cookie.startswith("refresh_token="):
                        new_refresh_token = cookie.split(";")[0].split("=", 1)[1]
                        break

                save_tokens(new_access_token, new_refresh_token)
                self.access_token = new_access_token

                request.headers["Authorization"] = f"Bearer {new_access_token}"
                yield request
