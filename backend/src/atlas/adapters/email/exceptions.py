"""Email exceptions - Email delivery errors."""


class EmailError(Exception):
    """Base exception for all email errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class EmailDeliveryError(EmailError):
    """Raised when email delivery fails."""

    def __init__(self, to_email: str, reason: str | None = None) -> None:
        self.to_email = to_email
        self.reason = reason
        message = f"Failed to deliver email to: {to_email}"
        if reason:
            message += f" - {reason}"
        super().__init__(message)


class EmailConfigurationError(EmailError):
    """Raised when email service is misconfigured."""

    def __init__(self, message: str = "Email service is not configured") -> None:
        super().__init__(message)
