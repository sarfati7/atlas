"""Console email service - Development implementation that prints to stdout."""

from atlas.adapters.email.interface import AbstractEmailService


class ConsoleEmailService(AbstractEmailService):
    """Email service that prints emails to console for development."""

    async def send_password_reset(self, to_email: str, reset_url: str) -> None:
        """Print password reset email to console."""
        print("========== PASSWORD RESET EMAIL ==========")
        print(f"To: {to_email}")
        print(f"Reset URL: {reset_url}")
        print("==========================================")
