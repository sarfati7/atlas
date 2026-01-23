"""Authentication routes - Registration, login, and password management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from atlas.domain.entities.user import User
from atlas.domain.interfaces import AbstractAuthService, AbstractUserRepository
from atlas.domain.value_objects.password import Password
from atlas.entrypoints.dependencies import (
    get_auth_service,
    get_user_repository,
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
    user_repo: Annotated[AbstractUserRepository, Depends(get_user_repository)],
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
    existing_email = await user_repo.get_by_email(body.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check for existing username
    existing_username = await user_repo.get_by_username(body.username)
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
    saved_user = await user_repo.save(user)

    return RegisterResponse(
        message="User created successfully",
        user_id=str(saved_user.id),
    )
