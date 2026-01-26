"""JWT-based authentication service with Argon2 password hashing."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import jwt
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pwdlib import PasswordHash

from atlas.adapters.authentication.interface import AbstractAuthService


class JWTAuthService(AbstractAuthService):
    """
    JWT authentication service implementation.

    Uses Argon2id for password hashing (via pwdlib) and PyJWT for tokens.
    Password reset tokens use itsdangerous for URL-safe time-limited tokens.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        password_reset_salt: str = "password-reset",
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days
        self._password_reset_salt = password_reset_salt

        self._password_hasher = PasswordHash.recommended()
        self._reset_serializer = URLSafeTimedSerializer(
            secret_key, salt=password_reset_salt
        )

    def hash_password(self, password: str) -> str:
        """Hash a plain-text password using Argon2id."""
        return self._password_hasher.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its Argon2id hash."""
        return self._password_hasher.verify(password, password_hash)

    def create_access_token(self, user_id: UUID, email: str) -> str:
        """Create a short-lived JWT access token."""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self._access_token_expire_minutes)

        payload = {
            "sub": str(user_id),
            "email": email,
            "type": "access",
            "iat": now,
            "exp": expire,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, user_id: UUID) -> str:
        """Create a long-lived JWT refresh token."""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self._refresh_token_expire_days)

        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": now,
            "exp": expire,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token, self._secret_key, algorithms=[self._algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def create_password_reset_token(self, user_id: UUID) -> str:
        """Create a URL-safe time-limited password reset token."""
        return self._reset_serializer.dumps(str(user_id))

    def verify_password_reset_token(
        self, token: str, max_age_seconds: int = 3600
    ) -> Optional[UUID]:
        """Verify password reset token and extract user ID."""
        try:
            user_id_str = self._reset_serializer.loads(token, max_age=max_age_seconds)
            return UUID(user_id_str)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        except ValueError:
            return None
