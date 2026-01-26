"""Email service interface - Abstract contract for email delivery."""

from abc import ABC, abstractmethod


class AbstractEmailService(ABC):
    """
    Abstract email service interface.

    Defines operations for sending various types of emails.
    """

    @abstractmethod
    async def send_password_reset(self, to_email: str, reset_url: str) -> None:
        """
        Send a password reset email.

        Args:
            to_email: Recipient email address
            reset_url: Full URL for password reset (includes token)
        """
        raise NotImplementedError
