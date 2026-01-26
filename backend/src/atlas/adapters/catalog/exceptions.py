"""Catalog exceptions - Git content repository errors."""


class CatalogError(Exception):
    """Base exception for all catalog errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ContentNotFoundError(CatalogError):
    """Raised when content at a path does not exist."""

    def __init__(self, path: str) -> None:
        self.path = path
        message = f"Content not found at path: {path}"
        super().__init__(message)


class VersionNotFoundError(CatalogError):
    """Raised when a requested version (commit SHA) does not exist."""

    def __init__(self, commit_sha: str, path: str | None = None) -> None:
        self.commit_sha = commit_sha
        self.path = path
        if path:
            message = f"Version '{commit_sha}' not found for path: {path}"
        else:
            message = f"Version '{commit_sha}' not found"
        super().__init__(message)


class CatalogConnectionError(CatalogError):
    """Raised when connection to catalog backend (e.g., GitHub) fails."""

    def __init__(self, message: str = "Failed to connect to catalog") -> None:
        super().__init__(message)


class ContentWriteError(CatalogError):
    """Raised when writing content to catalog fails."""

    def __init__(self, path: str, reason: str | None = None) -> None:
        self.path = path
        self.reason = reason
        message = f"Failed to write content at path: {path}"
        if reason:
            message += f" - {reason}"
        super().__init__(message)


class CatalogPermissionError(CatalogError):
    """Raised when GitHub token lacks required permissions."""

    def __init__(self, operation: str = "write") -> None:
        self.operation = operation
        message = (
            f"GitHub token does not have permission to {operation}. "
            "Please update the token in Admin → Settings with 'Contents: Read and write' permission."
        )
        super().__init__(message)
