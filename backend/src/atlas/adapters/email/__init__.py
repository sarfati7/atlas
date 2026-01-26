"""Email adapter - Email delivery implementations."""

from atlas.adapters.email.console import ConsoleEmailService
from atlas.adapters.email.exceptions import (
    EmailConfigurationError,
    EmailDeliveryError,
    EmailError,
)
from atlas.adapters.email.interface import AbstractEmailService
from atlas.adapters.email.smtp import SMTPEmailService

__all__ = [
    "AbstractEmailService",
    "ConsoleEmailService",
    "EmailConfigurationError",
    "EmailDeliveryError",
    "EmailError",
    "SMTPEmailService",
]
