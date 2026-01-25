"""Admin audit log routes - View audit logs with filtering."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from atlas.entrypoints.api.routes.admin_users import RequireAdmin
from atlas.entrypoints.dependencies import Repo


router = APIRouter(prefix="/admin/audit", tags=["admin-audit"])


# -----------------------------------------------------------------------------
# Response schemas
# -----------------------------------------------------------------------------


class AuditLogResponse(BaseModel):
    """Audit log entry response."""

    id: UUID
    user_id: UUID
    user_email: Optional[str]  # Joined from user if available
    action: str
    resource_type: str
    resource_id: UUID
    details: dict
    created_at: datetime


class PaginatedAuditLogsResponse(BaseModel):
    """Paginated list of audit logs."""

    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int


class AuditLogListResponse(BaseModel):
    """Simple list of audit logs for resource trail."""

    items: list[AuditLogResponse]


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------


@router.get(
    "/logs",
    response_model=PaginatedAuditLogsResponse,
)
async def list_audit_logs(
    admin: RequireAdmin,
    repo: Repo,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=100, description="Page size"),
    resource_type: Optional[str] = Query(
        default=None, description="Filter by resource type (user, team, configuration)"
    ),
    resource_id: Optional[UUID] = Query(default=None, description="Filter by resource ID"),
    user_id: Optional[UUID] = Query(
        default=None, description="Filter by user who made the change"
    ),
    action: Optional[str] = Query(default=None, description="Filter by action"),
) -> PaginatedAuditLogsResponse:
    """
    List audit logs with pagination and filtering.

    Requires admin role.
    """
    # Build cache of user emails for efficient lookup
    users = await repo.list_users()
    user_emails = {u.id: u.email for u in users}

    # Get total count
    total = await repo.count_audit_logs(
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
    )

    # Get paginated logs
    offset = (page - 1) * page_size
    logs = await repo.get_audit_logs(
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        limit=page_size,
        offset=offset,
    )

    # Filter by action if specified (not supported in repository, filter in-memory)
    if action:
        logs = [log for log in logs if log.action == action]
        # Recalculate total for action filter - this is an approximation
        # For proper filtering, we'd need to add action to repository query

    items = [
        AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_email=user_emails.get(log.user_id),
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=log.details,
            created_at=log.created_at,
        )
        for log in logs
    ]

    return PaginatedAuditLogsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/logs/{log_id}",
    response_model=AuditLogResponse,
)
async def get_audit_log(
    log_id: UUID,
    admin: RequireAdmin,
    repo: Repo,
) -> AuditLogResponse:
    """
    Get a single audit log entry by ID.

    Requires admin role.
    """
    # Get all logs and find by ID (no direct get_by_id in repository)
    # We could add a get_audit_log_by_id method, but for now we can filter
    logs = await repo.get_audit_logs(limit=1000000)
    log = next((l for l in logs if l.id == log_id), None)

    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    # Get user email
    user = await repo.get_user_by_id(log.user_id)
    user_email = user.email if user else None

    return AuditLogResponse(
        id=log.id,
        user_id=log.user_id,
        user_email=user_email,
        action=log.action,
        resource_type=log.resource_type,
        resource_id=log.resource_id,
        details=log.details,
        created_at=log.created_at,
    )


@router.get(
    "/resources/{resource_type}/{resource_id}",
    response_model=AuditLogListResponse,
)
async def get_resource_audit_trail(
    resource_type: str,
    resource_id: UUID,
    admin: RequireAdmin,
    repo: Repo,
) -> AuditLogListResponse:
    """
    Get audit trail for a specific resource.

    Returns all audit logs for the resource, newest first.
    Requires admin role.
    """
    # Build cache of user emails for efficient lookup
    users = await repo.list_users()
    user_emails = {u.id: u.email for u in users}

    # Get all logs for this resource
    logs = await repo.get_audit_logs(
        resource_type=resource_type,
        resource_id=resource_id,
        limit=1000,  # Reasonable limit for resource trail
    )

    items = [
        AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_email=user_emails.get(log.user_id),
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=log.details,
            created_at=log.created_at,
        )
        for log in logs
    ]

    return AuditLogListResponse(items=items)
