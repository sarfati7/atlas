"""Atlas CLI entry point."""

import typer

from atlas_cli import __version__

app = typer.Typer(
    name="atlas",
    help="Sync Claude configuration from Atlas platform",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"atlas-cli {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """Sync Claude configuration from Atlas platform."""
    pass


# Register command groups
from atlas_cli.commands import auth

app.add_typer(auth.app, name="auth")


def main() -> None:
    """Run the Atlas CLI application."""
    app()


if __name__ == "__main__":
    main()
