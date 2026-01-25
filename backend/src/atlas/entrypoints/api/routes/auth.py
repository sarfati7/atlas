"""Authentication routes - Registration, login, and password management."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from atlas.adapters.authentication import AbstractAuthService
from atlas.adapters.email import AbstractEmailService
from atlas.config import settings
from atlas.domain.entities.user import User
from atlas.domain.value_objects.password import Password
from atlas.entrypoints.dependencies import (
    CurrentUser,
    Repo,
    get_auth_service,
    get_email_service,
)

# Rate limiter for auth endpoints
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    email: EmailStr
    password: str
    username: str


class RegisterResponse(BaseModel):
    """Response for successful registration."""

    message: str
    user_id: str


class TokenResponse(BaseModel):
    """Response containing access token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """Response containing user information."""

    id: UUID
    email: str
    username: str
    role: str
    created_at: datetime


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class ForgotPasswordRequest(BaseModel):
    """Request body for password reset initiation."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request body for password reset completion."""

    token: str
    new_password: str


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("3/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    auth_service: Annotated[AbstractAuthService, Depends(get_auth_service)],
    repo: Repo,
) -> RegisterResponse:
    """
    Register a new user account.

    Creates a user with the provided email, username, and password.
    Password is hashed using Argon2id before storage.

    Rate limited to 3 requests per minute per IP.

    Raises:
        422: Password too short (< 8 characters)
        400: Email already registered
        400: Username already taken
    """
    # Validate password strength using Password value object
    try:
        Password(value=body.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    # Check for existing email
    existing_email = await repo.get_user_by_email(body.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check for existing username
    existing_username = await repo.get_user_by_username(body.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Hash password
    password_hash = auth_service.hash_password(body.password)

    # Create user entity
    user = User(
        email=body.email,
        username=body.username,
        password_hash=password_hash,
    )

    # Save user
    saved_user = await repo.save_user(user)

    return RegisterResponse(
        message="User created successfully",
        user_id=str(saved_user.id),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AbstractAuthService, Depends(get_auth_service)],
    repo: Repo,
) -> TokenResponse:
    """
    Authenticate user and return access token.

    Uses OAuth2 password flow. The 'username' field should contain the email.
    On successful login:
    - Returns access token in response body
    - Sets refresh token in HttpOnly cookie (7 day expiry)

    Rate limited to 5 requests per minute per IP.

    Raises:
        401: Incorrect email or password (generic message to prevent enumeration)
    """
    # Generic error message - same for wrong email OR wrong password
    # This prevents attackers from enumerating valid emails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Fetch user by email (form_data.username contains the email)
    user = await repo.get_user_by_email(form_data.username)

    # If user not found or has no password (OAuth-only user), fail
    if user is None or user.password_hash is None:
        raise credentials_exception

    # Verify password
    if not auth_service.verify_password(form_data.password, user.password_hash):
        raise credentials_exception

    # Create access token
    access_token = auth_service.create_access_token(user.id, user.email)

    # Create refresh token
    refresh_token = auth_service.create_refresh_token(user.id)

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.debug,  # Secure in production (HTTPS only)
        samesite="lax",  # Allows redirect from email links
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/api/v1/auth",  # Only sent to auth endpoints
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,  # Convert to seconds
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
)
async def logout(
    response: Response,
    current_user: CurrentUser,
) -> MessageResponse:
    """
    Log out the current user.

    Clears the refresh token cookie. The access token will remain valid
    until it expires (short-lived by design).

    Requires authentication.
    """
    # Delete refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
    )

    return MessageResponse(message="Logged out successfully")


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
    request: Request,
    auth_service: Annotated[AbstractAuthService, Depends(get_auth_service)],
    repo: Repo,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> TokenResponse:
    """
    Refresh access token using refresh token from cookie.

    The refresh token must be present in the HttpOnly cookie.
    Returns a new access token on success.

    Raises:
        401: Refresh token missing, invalid, expired, or user not found
    """
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify refresh token
    payload = auth_service.verify_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check token type is refresh
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user to ensure still exists
    user = await repo.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new access token
    access_token = auth_service.create_access_token(user.id, user.email)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_current_user_info(
    current_user: CurrentUser,
) -> UserResponse:
    """
    Get the current authenticated user's information.

    Requires authentication via Bearer token.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role.value,
        created_at=current_user.created_at,
    )


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    auth_service: Annotated[AbstractAuthService, Depends(get_auth_service)],
    email_service: Annotated[AbstractEmailService, Depends(get_email_service)],
    repo: Repo,
) -> MessageResponse:
    """
    Request a password reset email.

    If the email is registered, sends a password reset link.
    Always returns the same response regardless of whether the email exists
    (to prevent email enumeration attacks).

    Rate limited to 3 requests per minute per IP.
    """
    # Always return same message - never reveal if email exists
    response_message = "If that email is registered, you will receive a reset link"

    # Look up user by email
    user = await repo.get_user_by_email(body.email)

    if user is not None:
        # Generate password reset token (valid for 30 minutes)
        reset_token = auth_service.create_password_reset_token(user.id)

        # Build reset URL
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"

        # Send reset email (console or SMTP depending on config)
        await email_service.send_password_reset(body.email, reset_url)

    return MessageResponse(message=response_message)


@router.post(
    "/reset-password",
    response_model=MessageResponse,
)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    body: ResetPasswordRequest,
    auth_service: Annotated[AbstractAuthService, Depends(get_auth_service)],
    repo: Repo,
) -> MessageResponse:
    """
    Reset password using a valid reset token.

    The token must be obtained from the password reset email and is valid
    for 30 minutes. The new password must be at least 8 characters.

    Rate limited to 5 requests per minute per IP.

    Raises:
        422: New password too short (< 8 characters)
        400: Invalid or expired reset token
    """
    # Validate new password using Password value object
    try:
        Password(value=body.new_password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    # Verify token (30 minutes = 1800 seconds)
    user_id = auth_service.verify_password_reset_token(body.token, max_age_seconds=1800)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Fetch user by ID
    user = await repo.get_user_by_id(user_id)

    if user is None:
        # User was deleted after token was created
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Hash new password
    user.password_hash = auth_service.hash_password(body.new_password)

    # Save updated user
    await repo.save_user(user)

    return MessageResponse(message="Password successfully reset")
