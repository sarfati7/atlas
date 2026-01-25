"""Authentication commands for Atlas CLI."""

import typer
from httpx import ConnectError, HTTPStatusError

from atlas_cli import console
from atlas_cli.api.client import create_unauthenticated_client
from atlas_cli.storage.credentials import clear_tokens, is_authenticated, save_tokens

app = typer.Typer(name="auth", help="Authentication commands")


@app.command()
def login(
    email: str = typer.Option(..., prompt=True, help="Your Atlas email"),
    password: str = typer.Option(
        ...,
        prompt=True,
        hide_input=True,
        help="Your password",
    ),
) -> None:
    """Authenticate with your Atlas account.

    On success, stores access and refresh tokens in your OS keychain
    for use by subsequent commands.
    """
    with console.console.status("Authenticating..."):
        try:
            with create_unauthenticated_client() as client:
                response = client.post(
                    "/auth/login",
                    data={"username": email, "password": password},
                )

                if response.status_code == 401:
                    console.error("Invalid email or password")
                    raise typer.Exit(1)

                response.raise_for_status()

                data = response.json()
                access_token = data["access_token"]

                refresh_token = None
                for cookie in response.headers.get_list("set-cookie"):
                    if cookie.startswith("refresh_token="):
                        refresh_token = cookie.split(";")[0].split("=", 1)[1]
                        break

                if refresh_token is None:
                    console.error("Login failed: no refresh token received")
                    raise typer.Exit(1)

                save_tokens(access_token, refresh_token)

        except ConnectError:
            console.error("Could not connect to Atlas server")
            console.info("Check your network connection or ATLAS_API_URL setting")
            raise typer.Exit(1)
        except HTTPStatusError as e:
            if e.response.status_code == 401:
                console.error("Invalid email or password")
            else:
                console.error(f"Login failed: {e.response.status_code}")
            raise typer.Exit(1)

    console.success("Successfully logged in!")


@app.command()
def logout() -> None:
    """Log out and clear stored credentials.

    Removes all tokens from your OS keychain. You will need to
    log in again before running commands that require authentication.
    """
    clear_tokens()
    console.success("Logged out successfully")


@app.command()
def status() -> None:
    """Show current authentication status.

    Reports whether you are logged in based on the presence of
    stored credentials in your OS keychain.
    """
    if is_authenticated():
        console.success("Authenticated")
    else:
        console.info("Not logged in")
        console.info('Run "atlas auth login" to authenticate')
