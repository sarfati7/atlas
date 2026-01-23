"""SMTP email service - Production implementation using fastapi-mail."""

import logging
from typing import Optional

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from atlas.domain.interfaces.email_service import AbstractEmailService

logger = logging.getLogger(__name__)


class SMTPEmailService(AbstractEmailService):
    """
    Email service that sends emails via SMTP.

    Uses fastapi-mail for async email delivery.
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        email_from: str = "noreply@atlas.local",
    ) -> None:
        """
        Initialize SMTP email service.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port (default 587 for TLS)
            smtp_user: SMTP username (optional, for authenticated SMTP)
            smtp_password: SMTP password (optional)
            email_from: From address for outgoing emails
        """
        self._config = ConnectionConfig(
            MAIL_USERNAME=smtp_user or "",
            MAIL_PASSWORD=smtp_password or "",
            MAIL_FROM=email_from,
            MAIL_PORT=smtp_port,
            MAIL_SERVER=smtp_host,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=bool(smtp_user and smtp_password),
            VALIDATE_CERTS=True,
        )
        self._mail = FastMail(self._config)

    async def send_password_reset(self, to_email: str, reset_url: str) -> None:
        """
        Send a password reset email via SMTP.

        Handles connection errors gracefully (logs error, doesn't crash).
        This prevents revealing email existence through error responses.
        """
        html_body = f"""
        <html>
        <body>
            <h2>Reset Your Atlas Password</h2>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}">{reset_url}</a></p>
            <p>This link expires in 30 minutes.</p>
            <p>If you didn't request this password reset, you can safely ignore this email.</p>
        </body>
        </html>
        """

        message = MessageSchema(
            subject="Reset Your Atlas Password",
            recipients=[to_email],
            body=html_body,
            subtype=MessageType.html,
        )

        try:
            await self._mail.send_message(message)
            logger.info(f"Password reset email sent to {to_email}")
        except Exception as e:
            # Log error but don't crash - this prevents revealing email existence
            logger.error(f"Failed to send password reset email to {to_email}: {e}")
