"""Encryption utilities for storing secrets in the database."""

import base64
import hashlib

from cryptography.fernet import Fernet

from atlas.config import settings


def _get_encryption_key() -> bytes:
    """Derive a Fernet-compatible key from the application secret key."""
    key_hash = hashlib.sha256(settings.secret_key.encode()).digest()
    return base64.urlsafe_b64encode(key_hash)


def encrypt_value(value: str) -> str:
    """Encrypt a string value for secure storage."""
    fernet = Fernet(_get_encryption_key())
    encrypted = fernet.encrypt(value.encode())
    return encrypted.decode()


def decrypt_value(encrypted: str) -> str:
    """Decrypt a stored encrypted value."""
    fernet = Fernet(_get_encryption_key())
    decrypted = fernet.decrypt(encrypted.encode())
    return decrypted.decode()
