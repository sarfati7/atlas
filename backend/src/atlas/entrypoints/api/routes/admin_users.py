"""Admin user management routes - List, view, update role, and delete users."""

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from atlas.adapters.authorization import AbstractAuthorizationService, AuthorizationError
from atlas.domain.entities import AuditLog, Team
from atlas.domain.entities.user import User, UserRole
from atlas.entrypoints.dependencies import (
    AuthorizationSvc,
    CurrentUser,
    Repo,
)


router = APIRouter(prefix="/admin/users", tags=["admin-users"])


# -----------------------------------------------------------------------------
# Request/Response schemas
# -----------------------------------------------------------------------------


class UserResponse(BaseModel):
    """User response excluding password_hash."""

    id: UUID
    email: str
    username: str
    role: UserRole
    team_ids: list[UUID]
    created_at: datetime


class TeamResponse(BaseModel):
    """Team response for user details."""

    id: UUID
    name: str
    created_at: datetime


class UserDetailResponse(BaseModel):
    """User detail response with teams."""

    user: UserResponse
    teams: list[TeamResponse]


class PaginatedUsersResponse(BaseModel):
    """Paginated list of users."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int


class UpdateRoleRequest(BaseModel):
    """Request to update user role."""

    role: UserRole


# -----------------------------------------------------------------------------
# Admin dependency
# -----------------------------------------------------------------------------


async def require_admin(
    current_user: CurrentUser,
    auth_service: AuthorizationSvc,
) -> User:
    """Dependency that requires admin role."""
    try:
        await auth_service.require_admin(current_user)
    except AuthorizationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user


RequireAdmin = Annotated[User, Depends(require_admin)]


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------


def user_to_response(user: User) -> UserResponse:
    """Convert User entity to response, excluding password_hash."""
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role,
        team_ids=user.team_ids,
        created_at=user.created_at,
    )


def team_to_response(team: Team) -> TeamResponse:
    """Convert Team entity to response."""
    return TeamResponse(
        id=team.id,
        name=team.name,
        created_at=team.created_at,
    )


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------


@router.get(
    "/",
    response_model=PaginatedUsersResponse,
)
async def list_users(
    admin: RequireAdmin,
    repo: Repo,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(default=None, description="Search by email or username"),
) -> PaginatedUsersResponse:
    """
    List all users with pagination.

    Requires admin role.
    Supports search by email or username (case-insensitive).
    """
    all_users = await repo.list_users()

    # Apply search filter
    if search:
        search_lower = search.lower()
        all_users = [
            u for u in all_users
            if search_lower in u.email.lower() or search_lower in u.username.lower()
        ]

    total = len(all_users)

    # Apply pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_users = all_users[start:end]

    return PaginatedUsersResponse(
        items=[user_to_response(u) for u in paginated_users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
)
async def get_user(
    user_id: UUID,
    admin: RequireAdmin,
    repo: Repo,
) -> UserDetailResponse:
    """
    Get user details including their teams.

    Requires admin role.
    """
    user = await repo.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    teams = await repo.get_user_teams(user_id)

    return UserDetailResponse(
        user=user_to_response(user),
        teams=[team_to_response(t) for t in teams],
    )


@router.put(
    "/{user_id}/role",
    response_model=UserResponse,
)
async def update_user_role(
    user_id: UUID,
    body: UpdateRoleRequest,
    admin: RequireAdmin,
    repo: Repo,
) -> UserResponse:
    """
    Update a user's role.

    Requires admin role.
    Cannot demote self to prevent lockout.
    """
    user = await repo.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent self-demotion
    if user_id == admin.id and body.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote yourself",
        )

    old_role = user.role
    user.role = body.role
    saved_user = await repo.save_user(user)

    # Create audit log (fire-and-forget)
    try:
        audit_log = AuditLog(
            user_id=admin.id,
            action="user.role_changed",
            resource_type="user",
            resource_id=user_id,
            details={"old_role": old_role.value, "new_role": body.role.value},
        )
        await repo.save_audit_log(audit_log)
    except Exception:
        # Fire-and-forget: don't fail main operation on audit failure
        pass

    return user_to_response(saved_user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID,
    admin: RequireAdmin,
    repo: Repo,
) -> None:
    """
    Delete a user from the platform.

    Requires admin role.
    Cannot delete self.
    Also removes user from all teams and deletes their configuration.
    """
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )

    user = await repo.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Store user info for audit log before deletion
    user_info = {
        "email": user.email,
        "username": user.username,
        "team_ids": [str(tid) for tid in user.team_ids],
    }

    # Delete user's configuration if exists
    config = await repo.get_configuration_by_user_id(user_id)
    if config:
        await repo.delete_configuration(config.id)

    # Delete the user (team memberships handled by cascade)
    deleted = await repo.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Create audit log (fire-and-forget)
    try:
        audit_log = AuditLog(
            user_id=admin.id,
            action="user.deleted",
            resource_type="user",
            resource_id=user_id,
            details=user_info,
        )
        await repo.save_audit_log(audit_log)
    except Exception:
        # Fire-and-forget: don't fail main operation on audit failure
        pass
