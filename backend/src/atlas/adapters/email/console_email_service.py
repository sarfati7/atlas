"""Console email service - Development implementation that prints to stdout."""

from atlas.domain.interfaces.email_service import AbstractEmailService


class ConsoleEmailService(AbstractEmailService):
    """
    Email service that prints emails to console.

    Useful for development and testing without SMTP configuration.
    """

    async def send_password_reset(self, to_email: str, reset_url: str) -> None:
        """Print password reset email to console."""
        print("========== PASSWORD RESET EMAIL ==========")
        print(f"To: {to_email}")
        print(f"Reset URL: {reset_url}")
        print("==========================================")
