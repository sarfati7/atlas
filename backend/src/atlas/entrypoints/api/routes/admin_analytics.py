"""Admin analytics routes - Usage analytics and reporting."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel

from atlas.domain.entities import UsageEvent
from atlas.domain.entities.catalog_item import CatalogItemType
from atlas.entrypoints.api.routes.admin_users import RequireAdmin
from atlas.entrypoints.dependencies import Repo


router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


# -----------------------------------------------------------------------------
# Response schemas
# -----------------------------------------------------------------------------


class UsageSummaryResponse(BaseModel):
    """Overall usage summary statistics."""

    total_events: int
    total_users: int
    total_items: int
    events_today: int
    events_this_week: int
    events_this_month: int
    top_action: Optional[str]


class UsageByUserItem(BaseModel):
    """Usage count for a single user."""

    user_id: UUID
    user_email: Optional[str]
    count: int


class UsageByUserResponse(BaseModel):
    """Usage grouped by user."""

    items: list[UsageByUserItem]
    total: int


class UsageByItemItem(BaseModel):
    """Usage count for a single catalog item."""

    item_id: UUID
    item_type: str
    count: int


class UsageByItemResponse(BaseModel):
    """Usage grouped by catalog item."""

    items: list[UsageByItemItem]
    total: int


class UsageTimelineItem(BaseModel):
    """Usage count for a single day."""

    date: str
    count: int


class UsageTimelineResponse(BaseModel):
    """Usage over time."""

    items: list[UsageTimelineItem]


class UsageEventResponse(BaseModel):
    """A single usage event."""

    id: UUID
    user_id: UUID
    item_id: UUID
    item_type: str
    action: str
    metadata: dict
    created_at: datetime


class RecordEventRequest(BaseModel):
    """Request to record a usage event."""

    user_id: UUID
    item_id: UUID
    item_type: CatalogItemType
    action: str
    metadata: Optional[dict] = None


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------


@router.get(
    "/summary",
    response_model=UsageSummaryResponse,
)
async def get_usage_summary(
    admin: RequireAdmin,
    repo: Repo,
    start_date: Optional[datetime] = Query(default=None, description="Filter from date"),
    end_date: Optional[datetime] = Query(default=None, description="Filter to date"),
) -> UsageSummaryResponse:
    """
    Get overall usage summary with key metrics.

    Requires admin role.
    """
    from datetime import timedelta

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)

    # Get total counts
    total_events = await repo.count_usage_events(
        start_date=start_date,
        end_date=end_date,
    )
    events_today = await repo.count_usage_events(start_date=today_start)
    events_this_week = await repo.count_usage_events(start_date=week_start)
    events_this_month = await repo.count_usage_events(start_date=month_start)

    # Get unique users and items from stats
    user_stats = await repo.get_usage_stats(
        start_date=start_date,
        end_date=end_date,
        group_by="user",
    )
    item_stats = await repo.get_usage_stats(
        start_date=start_date,
        end_date=end_date,
        group_by="item",
    )

    total_users = len(user_stats)
    total_items = len(item_stats)

    # Get top action by sampling recent events
    recent_events = await repo.get_usage_events(
        start_date=start_date,
        end_date=end_date,
        limit=1000,
    )
    action_counts: dict[str, int] = {}
    for event in recent_events:
        action_counts[event.action] = action_counts.get(event.action, 0) + 1

    top_action = max(action_counts, key=action_counts.get) if action_counts else None

    return UsageSummaryResponse(
        total_events=total_events,
        total_users=total_users,
        total_items=total_items,
        events_today=events_today,
        events_this_week=events_this_week,
        events_this_month=events_this_month,
        top_action=top_action,
    )


@router.get(
    "/usage-by-user",
    response_model=UsageByUserResponse,
)
async def get_usage_by_user(
    admin: RequireAdmin,
    repo: Repo,
    start_date: Optional[datetime] = Query(default=None, description="Filter from date"),
    end_date: Optional[datetime] = Query(default=None, description="Filter to date"),
    limit: int = Query(default=20, ge=1, le=100, description="Max results"),
) -> UsageByUserResponse:
    """
    Get usage grouped by user, sorted by count descending.

    Requires admin role.
    """
    stats = await repo.get_usage_stats(
        start_date=start_date,
        end_date=end_date,
        group_by="user",
    )

    # Sort by count descending and limit
    stats.sort(key=lambda x: x.count, reverse=True)
    stats = stats[:limit]

    # Get user emails for display
    users = await repo.list_users()
    user_emails = {str(u.id): u.email for u in users}

    items = [
        UsageByUserItem(
            user_id=UUID(stat.key),
            user_email=user_emails.get(stat.key),
            count=stat.count,
        )
        for stat in stats
    ]

    return UsageByUserResponse(
        items=items,
        total=len(stats),
    )


@router.get(
    "/usage-by-item",
    response_model=UsageByItemResponse,
)
async def get_usage_by_item(
    admin: RequireAdmin,
    repo: Repo,
    start_date: Optional[datetime] = Query(default=None, description="Filter from date"),
    end_date: Optional[datetime] = Query(default=None, description="Filter to date"),
    item_type: Optional[CatalogItemType] = Query(default=None, description="Filter by type"),
    limit: int = Query(default=20, ge=1, le=100, description="Max results"),
) -> UsageByItemResponse:
    """
    Get usage grouped by catalog item, sorted by count descending.

    Requires admin role.
    """
    stats = await repo.get_usage_stats(
        start_date=start_date,
        end_date=end_date,
        group_by="item",
    )

    # Filter by item type if specified
    if item_type is not None:
        stats = [s for s in stats if s.item_type == item_type.value]

    # Sort by count descending and limit
    stats.sort(key=lambda x: x.count, reverse=True)
    stats = stats[:limit]

    items = [
        UsageByItemItem(
            item_id=UUID(stat.key),
            item_type=stat.item_type or "",
            count=stat.count,
        )
        for stat in stats
    ]

    return UsageByItemResponse(
        items=items,
        total=len(stats),
    )


@router.get(
    "/usage-timeline",
    response_model=UsageTimelineResponse,
)
async def get_usage_timeline(
    admin: RequireAdmin,
    repo: Repo,
    start_date: Optional[datetime] = Query(default=None, description="Filter from date"),
    end_date: Optional[datetime] = Query(default=None, description="Filter to date"),
) -> UsageTimelineResponse:
    """
    Get usage over time, grouped by day.

    Requires admin role.
    Returns data sorted by date ascending for chart display.
    """
    stats = await repo.get_usage_stats(
        start_date=start_date,
        end_date=end_date,
        group_by="day",
    )

    # Sort by date ascending
    stats.sort(key=lambda x: x.key)

    items = [
        UsageTimelineItem(
            date=stat.key,
            count=stat.count,
        )
        for stat in stats
    ]

    return UsageTimelineResponse(items=items)


@router.post(
    "/events",
    response_model=UsageEventResponse,
)
async def record_usage_event(
    body: RecordEventRequest,
    admin: RequireAdmin,
    repo: Repo,
) -> UsageEventResponse:
    """
    Record a new usage event.

    Requires admin role.
    This endpoint is primarily for CLI/external integrations.
    """
    event = UsageEvent(
        user_id=body.user_id,
        item_id=body.item_id,
        item_type=body.item_type,
        action=body.action,
        metadata=body.metadata or {},
    )

    saved_event = await repo.save_usage_event(event)

    return UsageEventResponse(
        id=saved_event.id,
        user_id=saved_event.user_id,
        item_id=saved_event.item_id,
        item_type=saved_event.item_type.value,
        action=saved_event.action,
        metadata=saved_event.metadata,
        created_at=saved_event.created_at,
    )
