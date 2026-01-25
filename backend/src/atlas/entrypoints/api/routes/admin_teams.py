"""Admin team management routes - Create, update, delete teams and manage members."""

import logging
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from atlas.adapters.authorization import AuthorizationError
from atlas.domain.entities import AuditLog, Team
from atlas.domain.entities.user import User, UserRole
from atlas.entrypoints.dependencies import (
    AuthorizationSvc,
    CurrentUser,
    Repo,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/teams", tags=["admin-teams"])


# -----------------------------------------------------------------------------
# Request/Response schemas
# -----------------------------------------------------------------------------


class TeamResponse(BaseModel):
    """Team response."""

    id: UUID
    name: str
    member_count: int
    created_at: datetime
    updated_at: datetime


class MemberResponse(BaseModel):
    """Team member response."""

    id: UUID
    email: str
    username: str
    role: UserRole


class TeamDetailResponse(BaseModel):
    """Team detail response with members."""

    team: TeamResponse
    members: list[MemberResponse]


class PaginatedTeamsResponse(BaseModel):
    """Paginated list of teams."""

    items: list[TeamResponse]
    total: int
    page: int
    page_size: int


class CreateTeamRequest(BaseModel):
    """Request to create a team."""

    name: str


class UpdateTeamRequest(BaseModel):
    """Request to update a team."""

    name: str


class AddMemberRequest(BaseModel):
    """Request to add a member to a team."""

    user_id: UUID


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


def team_to_response(team: Team) -> TeamResponse:
    """Convert Team entity to response."""
    return TeamResponse(
        id=team.id,
        name=team.name,
        member_count=team.member_count,
        created_at=team.created_at,
        updated_at=team.updated_at,
    )


def user_to_member_response(user: User) -> MemberResponse:
    """Convert User entity to member response."""
    return MemberResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role,
    )


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------


@router.get(
    "/",
    response_model=PaginatedTeamsResponse,
)
async def list_teams(
    admin: RequireAdmin,
    repo: Repo,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Page size"),
) -> PaginatedTeamsResponse:
    """
    List all teams with pagination.

    Requires admin role.
    """
    all_teams = await repo.list_teams()
    total = len(all_teams)

    # Apply pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_teams = all_teams[start:end]

    return PaginatedTeamsResponse(
        items=[team_to_response(t) for t in paginated_teams],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_team(
    body: CreateTeamRequest,
    admin: RequireAdmin,
    repo: Repo,
) -> TeamResponse:
    """
    Create a new team.

    Requires admin role.
    Team name must be unique.
    """
    # Check for name collision
    existing = await repo.get_team_by_name(body.name)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team with this name already exists",
        )

    team = Team(name=body.name)
    saved_team = await repo.save_team(team)

    # Create audit log (fire-and-forget)
    try:
        audit_log = AuditLog(
            user_id=admin.id,
            action="team.created",
            resource_type="team",
            resource_id=saved_team.id,
            details={"name": saved_team.name},
        )
        await repo.save_audit_log(audit_log)
    except Exception as e:
        logger.warning(f"Failed to create audit log for team creation: {e}")

    return team_to_response(saved_team)


@router.get(
    "/{team_id}",
    response_model=TeamDetailResponse,
)
async def get_team(
    team_id: UUID,
    admin: RequireAdmin,
    repo: Repo,
) -> TeamDetailResponse:
    """
    Get team details including members.

    Requires admin role.
    """
    team = await repo.get_team_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Get members
    members = []
    for member_id in team.member_ids:
        user = await repo.get_user_by_id(member_id)
        if user:
            members.append(user_to_member_response(user))

    return TeamDetailResponse(
        team=team_to_response(team),
        members=members,
    )


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
)
async def update_team(
    team_id: UUID,
    body: UpdateTeamRequest,
    admin: RequireAdmin,
    repo: Repo,
) -> TeamResponse:
    """
    Update a team's name.

    Requires admin role.
    Team name must be unique.
    """
    team = await repo.get_team_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Check for name collision (if name is changing)
    if body.name != team.name:
        existing = await repo.get_team_by_name(body.name)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Team with this name already exists",
            )

    old_name = team.name
    team.name = body.name
    team.updated_at = datetime.utcnow()
    saved_team = await repo.save_team(team)

    # Create audit log (fire-and-forget)
    try:
        audit_log = AuditLog(
            user_id=admin.id,
            action="team.updated",
            resource_type="team",
            resource_id=team_id,
            details={"old_name": old_name, "new_name": body.name},
        )
        await repo.save_audit_log(audit_log)
    except Exception as e:
        logger.warning(f"Failed to create audit log for team update: {e}")

    return team_to_response(saved_team)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_team(
    team_id: UUID,
    admin: RequireAdmin,
    repo: Repo,
) -> None:
    """
    Delete a team.

    Requires admin role.
    Also removes team from all users' team_ids.
    """
    team = await repo.get_team_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Store team info for audit log
    team_info = {
        "name": team.name,
        "member_count": team.member_count,
        "member_ids": [str(mid) for mid in team.member_ids],
    }

    # Remove team from all users who are members
    for member_id in team.member_ids:
        user = await repo.get_user_by_id(member_id)
        if user:
            user.remove_from_team(team_id)
            await repo.save_user(user)

    deleted = await repo.delete_team(team_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Create audit log (fire-and-forget)
    try:
        audit_log = AuditLog(
            user_id=admin.id,
            action="team.deleted",
            resource_type="team",
            resource_id=team_id,
            details=team_info,
        )
        await repo.save_audit_log(audit_log)
    except Exception as e:
        logger.warning(f"Failed to create audit log for team deletion: {e}")


@router.post(
    "/{team_id}/members",
    response_model=TeamDetailResponse,
)
async def add_member(
    team_id: UUID,
    body: AddMemberRequest,
    admin: RequireAdmin,
    repo: Repo,
) -> TeamDetailResponse:
    """
    Add a user to a team.

    Requires admin role.
    """
    team = await repo.get_team_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    user = await repo.get_user_by_id(body.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if already a member
    if team.has_member(body.user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this team",
        )

    # Add member to team and team to user
    team.add_member(body.user_id)
    user.add_to_team(team_id)

    await repo.save_team(team)
    await repo.save_user(user)

    # Create audit log (fire-and-forget)
    try:
        audit_log = AuditLog(
            user_id=admin.id,
            action="team.member_added",
            resource_type="team",
            resource_id=team_id,
            details={
                "added_user_id": str(body.user_id),
                "added_user_email": user.email,
            },
        )
        await repo.save_audit_log(audit_log)
    except Exception as e:
        logger.warning(f"Failed to create audit log for member addition: {e}")

    # Get updated team with members
    return await get_team(team_id, admin, repo)


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_member(
    team_id: UUID,
    user_id: UUID,
    admin: RequireAdmin,
    repo: Repo,
) -> None:
    """
    Remove a user from a team.

    Requires admin role.
    """
    team = await repo.get_team_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    user = await repo.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if actually a member
    if not team.has_member(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this team",
        )

    # Remove member from team and team from user
    team.remove_member(user_id)
    user.remove_from_team(team_id)

    await repo.save_team(team)
    await repo.save_user(user)

    # Create audit log (fire-and-forget)
    try:
        audit_log = AuditLog(
            user_id=admin.id,
            action="team.member_removed",
            resource_type="team",
            resource_id=team_id,
            details={
                "removed_user_id": str(user_id),
                "removed_user_email": user.email,
            },
        )
        await repo.save_audit_log(audit_log)
    except Exception as e:
        logger.warning(f"Failed to create audit log for member removal: {e}")
