"""Password value object - Validates password strength requirements."""

from pydantic import BaseModel, field_validator


class Password(BaseModel):
    """
    Password value object.

    Validates password meets minimum security requirements before use.
    This is used for input validation, NOT for storage (use password_hash).
    """

    value: str

    @field_validator("value")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Enforce minimum password requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
