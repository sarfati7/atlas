# Phase 2: Authentication - Research

**Researched:** 2026-01-23
**Domain:** User Authentication (JWT, Password Hashing, Session Management)
**Confidence:** HIGH

## Summary

This research covers authentication implementation for a FastAPI backend following DDD/Clean Architecture patterns. The established approach in 2025/2026 is JWT-based authentication using the OAuth2 Password Bearer flow, with Argon2id for password hashing (replacing bcrypt as the modern standard), and HttpOnly cookies for secure token storage.

The key finding is that FastAPI's official documentation now recommends **pwdlib** with Argon2 for password hashing and **PyJWT** for token handling. This represents a shift from the older passlib/bcrypt combination. For password reset, **itsdangerous** provides secure time-limited token generation without requiring database storage.

**Primary recommendation:** Use JWT access tokens (15-30 min expiry) with refresh tokens in HttpOnly cookies, Argon2id password hashing via pwdlib, and itsdangerous for password reset tokens. Structure authentication as an Application Service following the existing DDD patterns.

## Standard Stack

The established libraries/tools for FastAPI authentication:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyJWT | 2.10.1 | JWT token encoding/decoding | Official FastAPI docs recommendation, RFC 7519 compliant |
| pwdlib[argon2] | 0.3.0 | Password hashing (Argon2id) | FastAPI official docs, replaces passlib, modern memory-hard algorithm |
| itsdangerous | 2.2.0 | Timed tokens for password reset | Pallets project, no DB storage needed, secure serialization |
| fastapi-mail | 1.6.1 | Async email sending | FastAPI-native, supports templates, background tasks |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| slowapi | 0.1.9 | Rate limiting | Protect login/register endpoints from brute force |
| fastapi-csrf-protect | latest | CSRF protection | Only if using cookie-based auth with web frontend |
| argon2-cffi | 25.1.0 | Direct Argon2 access | Alternative to pwdlib if more control needed |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pwdlib | passlib + bcrypt | passlib has Python 3.13+ compatibility issues; bcrypt lacks memory-hardness |
| PyJWT | python-jose | python-jose has cryptography backend but PyJWT is simpler and official recommendation |
| itsdangerous | JWT for reset tokens | itsdangerous is simpler for single-use tokens; JWT requires blacklist for revocation |
| slowapi | fastapi-limiter | fastapi-limiter requires Redis; slowapi supports in-memory for simpler setups |

**Installation:**
```bash
pip install "pyjwt>=2.10.0" "pwdlib[argon2]>=0.3.0" "itsdangerous>=2.2.0" "fastapi-mail>=1.6.0" "slowapi>=0.1.9"
```

## Architecture Patterns

### Recommended Project Structure (DDD/Clean Architecture)

```
backend/src/atlas/
├── domain/
│   ├── entities/
│   │   └── user.py              # Add password_hash field
│   ├── value_objects/
│   │   ├── email.py             # Already exists
│   │   └── password.py          # NEW: Password validation rules
│   └── interfaces/
│       ├── user_repository.py   # Already exists
│       ├── auth_service.py      # NEW: Abstract auth service interface
│       └── email_service.py     # NEW: Abstract email service interface
├── application/
│   └── services/
│       └── auth_service.py      # NEW: Authentication use cases
├── adapters/
│   ├── auth/
│   │   ├── jwt_auth_service.py  # NEW: JWT implementation
│   │   └── password_hasher.py   # NEW: Argon2 password hashing
│   ├── email/
│   │   ├── smtp_email_service.py    # NEW: Real SMTP implementation
│   │   └── console_email_service.py # NEW: Dev/test implementation (prints to console)
│   └── in_memory/
│       └── repositories/
│           └── ...              # Existing in-memory repos for testing
└── entrypoints/
    ├── api/
    │   └── routes/
    │       └── auth.py          # NEW: Auth endpoints
    └── dependencies.py          # Add auth dependencies
```

### Pattern 1: Authentication Service Interface (Domain Layer)

**What:** Abstract interface defining authentication operations
**When to use:** Always - keeps domain clean of implementation details

```python
# domain/interfaces/auth_service.py
from abc import ABC, abstractmethod
from uuid import UUID
from atlas.domain.entities.user import User

class AbstractAuthService(ABC):
    """Authentication service interface - domain layer."""

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """Hash a plain text password."""
        raise NotImplementedError

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        raise NotImplementedError

    @abstractmethod
    def create_access_token(self, user_id: UUID, expires_minutes: int = 30) -> str:
        """Create a JWT access token for a user."""
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, user_id: UUID, expires_days: int = 7) -> str:
        """Create a JWT refresh token for a user."""
        raise NotImplementedError

    @abstractmethod
    def verify_token(self, token: str) -> UUID | None:
        """Verify a token and return user_id if valid, None otherwise."""
        raise NotImplementedError

    @abstractmethod
    def create_password_reset_token(self, email: str) -> str:
        """Create a time-limited password reset token."""
        raise NotImplementedError

    @abstractmethod
    def verify_password_reset_token(self, token: str, max_age_seconds: int = 1800) -> str | None:
        """Verify reset token and return email if valid."""
        raise NotImplementedError
```

### Pattern 2: JWT Auth Implementation (Adapters Layer)

**What:** Concrete JWT implementation of auth service
**When to use:** Production and testing with real JWT handling

```python
# adapters/auth/jwt_auth_service.py
from datetime import datetime, timedelta, timezone
from uuid import UUID
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from atlas.config import settings
from atlas.domain.interfaces.auth_service import AbstractAuthService

class JWTAuthService(AbstractAuthService):
    """JWT-based authentication service implementation."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        password_reset_salt: str = "password-reset"
    ):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._password_hash = PasswordHash.recommended()
        self._reset_serializer = URLSafeTimedSerializer(secret_key)
        self._reset_salt = password_reset_salt

    def hash_password(self, plain_password: str) -> str:
        return self._password_hash.hash(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._password_hash.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: UUID, expires_minutes: int = 30) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, user_id: UUID, expires_days: int = 7) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=expires_days)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh"
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def verify_token(self, token: str) -> UUID | None:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            user_id = payload.get("sub")
            if user_id:
                return UUID(user_id)
        except InvalidTokenError:
            pass
        return None

    def create_password_reset_token(self, email: str) -> str:
        return self._reset_serializer.dumps(email, salt=self._reset_salt)

    def verify_password_reset_token(self, token: str, max_age_seconds: int = 1800) -> str | None:
        try:
            return self._reset_serializer.loads(
                token, salt=self._reset_salt, max_age=max_age_seconds
            )
        except (SignatureExpired, BadSignature):
            return None
```

### Pattern 3: FastAPI Dependency for Current User

**What:** Dependency injection pattern for getting authenticated user
**When to use:** All protected endpoints

```python
# entrypoints/dependencies.py (additions)
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from atlas.domain.entities.user import User
from atlas.domain.interfaces.auth_service import AbstractAuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_auth_service() -> AbstractAuthService:
    """Provide auth service implementation."""
    from atlas.adapters.auth.jwt_auth_service import JWTAuthService
    return JWTAuthService(secret_key=settings.secret_key)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AbstractAuthService, Depends(get_auth_service)],
    user_repo: Annotated[AbstractUserRepository, Depends(get_user_repository)],
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = auth_service.verify_token(token)
    if user_id is None:
        raise credentials_exception

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user

# Type alias for route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
AuthService = Annotated[AbstractAuthService, Depends(get_auth_service)]
```

### Pattern 4: Auth Routes Structure

**What:** RESTful auth endpoint structure
**When to use:** Standard auth API design

```python
# entrypoints/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register")
async def register(
    email: str,
    password: str,
    username: str,
    auth_service: AuthService,
    user_repo: UserRepo,
) -> dict:
    """Create a new user account."""
    # Check if user exists
    # Hash password
    # Create user
    # Return success (don't auto-login, require explicit login)
    pass

@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService,
    user_repo: UserRepo,
    response: Response,
) -> dict:
    """Authenticate user and return tokens."""
    # Verify credentials
    # Create access and refresh tokens
    # Set refresh token in HttpOnly cookie
    # Return access token in response body
    pass

@router.post("/logout")
async def logout(
    response: Response,
    current_user: CurrentUser,
) -> dict:
    """Log out current user."""
    # Clear refresh token cookie
    pass

@router.post("/refresh")
async def refresh_token(
    # Get refresh token from cookie
) -> dict:
    """Get new access token using refresh token."""
    pass

@router.post("/forgot-password")
async def forgot_password(
    email: str,
    auth_service: AuthService,
    email_service: EmailService,
    user_repo: UserRepo,
) -> dict:
    """Request password reset email."""
    # Generate reset token
    # Send email with reset link
    # Always return success (don't reveal if email exists)
    pass

@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    auth_service: AuthService,
    user_repo: UserRepo,
) -> dict:
    """Reset password using token from email."""
    # Verify token
    # Hash new password
    # Update user
    pass
```

### Anti-Patterns to Avoid

- **Storing JWT secret in code:** Always use environment variables via pydantic-settings
- **Not validating password strength:** Add minimum requirements (length, complexity)
- **Returning different errors for wrong email vs wrong password:** Reveals valid emails to attackers
- **Storing access tokens in localStorage:** Vulnerable to XSS; use HttpOnly cookies or in-memory
- **Long-lived access tokens:** Keep access tokens short (15-30 min), use refresh tokens for sessions
- **Not rate limiting auth endpoints:** Enables brute force attacks
- **Using `==` for secret comparison:** Use `secrets.compare_digest()` for timing attack resistance

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | Custom hash function | pwdlib with Argon2 | Timing attacks, rainbow tables, GPU resistance |
| JWT tokens | Manual base64 encoding | PyJWT | Signature verification, expiration handling |
| Email sending | Raw SMTP connections | fastapi-mail | Async support, template rendering, connection pooling |
| Rate limiting | Request counters | slowapi | Distributed counting, flexible limits, proper key extraction |
| Reset tokens | Random strings in DB | itsdangerous | Cryptographic signatures, no DB storage needed, automatic expiration |
| Password validation | Regex patterns | Pydantic validators | Centralized rules, clear error messages |

**Key insight:** Authentication is a solved problem with well-vetted libraries. Hand-rolling any component introduces security vulnerabilities that take years to discover.

## Common Pitfalls

### Pitfall 1: Timing Attacks on Password Verification

**What goes wrong:** Using standard string comparison (`==`) for passwords or tokens reveals information through response timing
**Why it happens:** Python's `==` short-circuits on first character mismatch
**How to avoid:** Password hashing libraries handle this; for any manual comparison use `secrets.compare_digest()`
**Warning signs:** Inconsistent response times for valid vs invalid credentials

### Pitfall 2: JWT Token Revocation

**What goes wrong:** User logs out but JWT remains valid until expiration
**Why it happens:** JWTs are stateless - no server-side tracking by default
**How to avoid:**
- Keep access token lifetime short (15-30 min)
- Use refresh tokens in HttpOnly cookies that can be invalidated server-side
- For immediate revocation needs, maintain a token blacklist in Redis
**Warning signs:** Users complaining they can't "really" log out

### Pitfall 3: Password Reset Token Reuse

**What goes wrong:** Same reset token can be used multiple times
**Why it happens:** Token not invalidated after use
**How to avoid:**
- Include user's current password hash in token salt (changes on reset)
- Or store one-time-use flag in database
**Warning signs:** Security audit finds replay attack vulnerability

### Pitfall 4: Email Enumeration via Registration/Reset

**What goes wrong:** Attackers can determine which emails are registered
**Why it happens:** Different error messages for "email exists" vs "email not found"
**How to avoid:** Always return same response regardless of email existence
**Warning signs:** Seeing patterns like "This email is already registered" in UI

### Pitfall 5: Missing CSRF Protection with Cookies

**What goes wrong:** Authenticated requests can be forged from other sites
**Why it happens:** Cookies are automatically sent with requests
**How to avoid:** Use SameSite=Strict cookies, add CSRF tokens for state-changing operations
**Warning signs:** Cookie-based auth without SameSite attribute

### Pitfall 6: Storing Secrets in Code

**What goes wrong:** JWT secret key committed to git
**Why it happens:** Quick prototyping, forgetting to externalize
**How to avoid:** Always use environment variables via pydantic-settings
**Warning signs:** Hardcoded strings that look like secrets in source code

## Code Examples

### Complete Login Flow

```python
# Source: FastAPI official docs pattern + best practices
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from atlas.config import settings
from atlas.domain.entities.user import User
from atlas.entrypoints.dependencies import AuthService, UserRepo

router = APIRouter(prefix="/auth", tags=["authentication"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService,
    user_repo: UserRepo,
    response: Response,
) -> TokenResponse:
    """Authenticate user and return tokens."""
    # Get user by email (username field in OAuth2 form)
    user = await user_repo.get_by_email(form_data.username)

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not auth_service.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Requires HTTPS
        samesite="strict",
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
        path="/api/v1/auth/refresh",  # Only sent to refresh endpoint
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )
```

### Password Reset Flow

```python
# Source: itsdangerous + fastapi-mail pattern
from pydantic import BaseModel, EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService,
    email_service: EmailService,
    user_repo: UserRepo,
) -> dict:
    """Request password reset email."""
    # Always return success to prevent email enumeration
    user = await user_repo.get_by_email(request.email)

    if user:
        # Generate reset token
        reset_token = auth_service.create_password_reset_token(request.email)
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"

        # Send email (fire and forget in background)
        await email_service.send_password_reset(
            to_email=request.email,
            reset_url=reset_url,
        )

    # Same response whether user exists or not
    return {"message": "If that email is registered, you will receive a reset link"}

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService,
    user_repo: UserRepo,
) -> dict:
    """Reset password using token from email."""
    # Verify token (30 min expiry)
    email = auth_service.verify_password_reset_token(
        request.token,
        max_age_seconds=1800
    )

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = await user_repo.get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Update password
    user.password_hash = auth_service.hash_password(request.new_password)
    await user_repo.save(user)

    return {"message": "Password successfully reset"}
```

### Rate Limiting Auth Endpoints

```python
# Source: slowapi documentation
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # 5 attempts per minute per IP
async def login(
    request: Request,  # Required for slowapi
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService,
    user_repo: UserRepo,
    response: Response,
) -> TokenResponse:
    # ... login logic
    pass

@router.post("/register")
@limiter.limit("3/minute")  # 3 registrations per minute per IP
async def register(
    request: Request,
    # ... params
) -> dict:
    # ... register logic
    pass
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| passlib + bcrypt | pwdlib + Argon2id | 2024-2025 | Better GPU resistance, official FastAPI recommendation |
| python-jose | PyJWT | 2024 | Simpler API, faster, better maintained |
| localStorage for tokens | HttpOnly cookies + memory | 2023+ | XSS protection, better security posture |
| bcrypt alone | Argon2id | 2023+ | Memory-hard algorithm, PHC winner |
| Session tokens in DB | Stateless JWT + refresh rotation | 2022+ | Scalability, no DB lookup per request |

**Deprecated/outdated:**
- **passlib:** Maintenance issues with Python 3.13+, FastAPI docs now recommend pwdlib
- **python-jose:** Still works but PyJWT is simpler and officially recommended
- **bcrypt alone:** Still secure but Argon2id is the modern standard for new projects
- **Storing JWT in localStorage:** Known XSS vulnerability, use HttpOnly cookies

## Open Questions

Things that couldn't be fully resolved:

1. **Refresh Token Storage Strategy**
   - What we know: HttpOnly cookies are secure, DB storage enables revocation
   - What's unclear: Whether to store refresh tokens in DB or use token rotation
   - Recommendation: Start with cookie-only (stateless), add DB tracking if revocation needed

2. **Email Service Selection**
   - What we know: fastapi-mail works well, supports SMTP
   - What's unclear: Production email service (SendGrid, AWS SES, etc.)
   - Recommendation: Abstract behind interface, use console output for dev/test

3. **Password Strength Requirements**
   - What we know: NIST 2024 recommends minimum 8 chars, no complexity rules
   - What's unclear: Project-specific requirements
   - Recommendation: Start with 8 char minimum, add zxcvbn for strength meter later

## Sources

### Primary (HIGH confidence)
- [FastAPI Official Docs - OAuth2 JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) - Complete implementation pattern
- [PyPI: pwdlib 0.3.0](https://pypi.org/project/pwdlib/) - Official password hashing library
- [PyPI: PyJWT 2.10.1](https://pypi.org/project/pyjwt/) - JWT implementation
- [PyPI: itsdangerous 2.2.0](https://pypi.org/project/itsdangerous/) - Timed token serialization
- [PyPI: fastapi-mail 1.6.1](https://pypi.org/project/fastapi-mail/) - Email library
- [PyPI: slowapi 0.1.9](https://pypi.org/project/slowapi/) - Rate limiting
- [Python secrets module](https://docs.python.org/3/library/secrets.html) - Timing attack prevention

### Secondary (MEDIUM confidence)
- [Better Stack: Authentication Guide](https://betterstack.com/community/guides/scaling-python/authentication-fastapi/) - Patterns overview
- [TestDriven.io: FastAPI JWT Auth](https://testdriven.io/blog/fastapi-jwt-auth/) - Implementation tutorial
- [JWT Storage Best Practices](https://workos.com/blog/secure-jwt-storage) - Cookie vs localStorage analysis
- [GitHub: fastapi-clean-example](https://github.com/ivan-borovets/fastapi-clean-example) - DDD auth patterns

### Tertiary (LOW confidence)
- Various Medium articles on FastAPI auth patterns
- Stack Overflow discussions on token storage

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - FastAPI official docs + PyPI verified versions
- Architecture: HIGH - Follows existing project DDD patterns
- Pitfalls: HIGH - Well-documented security concerns with official sources
- Code examples: HIGH - Based on official FastAPI documentation patterns

**Research date:** 2026-01-23
**Valid until:** 2026-04-23 (3 months - auth libraries evolve slowly)
