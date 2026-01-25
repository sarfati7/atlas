"""Console output utilities with rich formatting."""

from rich.console import Console

console = Console()


def info(message: str) -> None:
    """Print an informational message."""
    console.print(f"[blue]{message}[/blue]")


def success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]{message}[/green]")


def error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]{message}[/red]")


def warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]{message}[/yellow]")
