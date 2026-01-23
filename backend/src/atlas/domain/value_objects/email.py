"""Email value object - Validated and immutable email address."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """
    Email value object.

    Immutable wrapper around email string with basic format validation.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate email format after initialization."""
        if not self._is_valid_format(self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    @staticmethod
    def _is_valid_format(email: str) -> bool:
        """Check if email has valid basic format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        """Return the email as string."""
        return self.value

    @property
    def domain(self) -> str:
        """Extract domain from email address."""
        return self.value.split("@")[1]

    @property
    def local_part(self) -> str:
        """Extract local part (before @) from email address."""
        return self.value.split("@")[0]
