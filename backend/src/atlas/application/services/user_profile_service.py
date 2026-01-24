"""User profile service - Aggregation and configuration inheritance."""

import asyncio
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from atlas.domain.entities import (
    CatalogItem,
    CatalogItemType,
    EffectiveConfiguration,
    Team,
)
from atlas.domain.interfaces import (
    AbstractCatalogRepository,
    AbstractConfigurationRepository,
    AbstractContentRepository,
    AbstractTeamRepository,
    AbstractUserRepository,
)


# Well-known configuration paths
ORG_CONFIG_PATH = "configs/organization/claude.md"


class UserNotFoundError(Exception):
    """Raised when user doesn't exist."""

    pass


class TeamSummary(BaseModel):
    """Summary view of a team for dashboard display."""

    id: UUID
    name: str
    member_count: int


class CatalogItemSummary(BaseModel):
    """Summary view of a catalog item."""

    id: UUID
    type: CatalogItemType
    name: str
    description: str


class UserDashboard(BaseModel):
    """Aggregated dashboard data for a user."""

    user_id: UUID
    username: str
    email: str
    teams: list[TeamSummary]
    available_skills: int
    available_mcps: int
    available_tools: int
    has_configuration: bool
    configuration_updated_at: Optional[datetime]


class UserProfileService:
    """
    Service layer for user profile operations.

    Aggregates data from multiple repositories to provide:
    - Dashboard summary (user info, teams, item counts, config status)
    - Available items filtered by team membership
    - Effective configuration merged from org/team/user levels
    """

    def __init__(
        self,
        user_repo: AbstractUserRepository,
        team_repo: AbstractTeamRepository,
        catalog_repo: AbstractCatalogRepository,
        config_repo: AbstractConfigurationRepository,
        content_repo: AbstractContentRepository,
    ) -> None:
        self._user_repo = user_repo
        self._team_repo = team_repo
        self._catalog_repo = catalog_repo
        self._config_repo = config_repo
        self._content_repo = content_repo

    def _get_team_config_path(self, team_id: UUID) -> str:
        """Generate git path for team's configuration."""
        return f"configs/teams/{team_id}/claude.md"

    def _filter_available_items(
        self, items: list[CatalogItem], team_ids: list[UUID]
    ) -> list[CatalogItem]:
        """Filter items to those available to user (company-wide + user's teams)."""
        return [
            item
            for item in items
            if item.team_id is None or item.team_id in team_ids
        ]

    def _count_by_type(
        self, items: list[CatalogItem]
    ) -> tuple[int, int, int]:
        """Count items by type (skills, mcps, tools)."""
        skills = sum(1 for item in items if item.type == CatalogItemType.SKILL)
        mcps = sum(1 for item in items if item.type == CatalogItemType.MCP)
        tools = sum(1 for item in items if item.type == CatalogItemType.TOOL)
        return skills, mcps, tools

    async def get_dashboard(self, user_id: UUID) -> UserDashboard:
        """
        Get aggregated dashboard data for a user.

        Fetches user info, teams, available item counts, and config status.
        Uses parallel fetches where possible for performance.
        """
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")

        # Parallel fetch: teams, all items, user config
        teams_task = asyncio.gather(
            *[self._team_repo.get_by_id(tid) for tid in user.team_ids]
        )
        items_task = self._catalog_repo.list()
        config_task = self._config_repo.get_by_user_id(user_id)

        teams_results, all_items, config = await asyncio.gather(
            teams_task, items_task, config_task
        )

        # Filter out None teams (in case of data inconsistency)
        teams: list[Team] = [t for t in teams_results if t is not None]

        # Filter available items and count by type
        available_items = self._filter_available_items(all_items, user.team_ids)
        skills, mcps, tools = self._count_by_type(available_items)

        # Build team summaries
        team_summaries = [
            TeamSummary(id=team.id, name=team.name, member_count=team.member_count)
            for team in teams
        ]

        return UserDashboard(
            user_id=user.id,
            username=user.username,
            email=user.email,
            teams=team_summaries,
            available_skills=skills,
            available_mcps=mcps,
            available_tools=tools,
            has_configuration=config is not None,
            configuration_updated_at=config.updated_at if config else None,
        )

    async def get_available_items(self, user_id: UUID) -> list[CatalogItemSummary]:
        """
        Get catalog items available to a user.

        Returns items that are company-wide (team_id=None) or belong to user's teams.
        Returns empty list if user doesn't exist (graceful degradation).
        """
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            return []

        all_items = await self._catalog_repo.list()
        available_items = self._filter_available_items(all_items, user.team_ids)

        return [
            CatalogItemSummary(
                id=item.id,
                type=item.type,
                name=item.name,
                description=item.description,
            )
            for item in available_items
        ]

    async def get_effective_configuration(
        self, user_id: UUID
    ) -> EffectiveConfiguration:
        """
        Get merged configuration from org -> team -> user levels.

        Fetches configuration content from all levels and merges with section markers.
        Missing configs are treated as empty strings.
        """
        # Fetch user's teams and config metadata in parallel
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            # Return empty configuration for non-existent user
            return EffectiveConfiguration(
                content="", org_content="", team_content="", user_content=""
            )

        teams_task = asyncio.gather(
            *[self._team_repo.get_by_id(tid) for tid in user.team_ids]
        )
        config_task = self._config_repo.get_by_user_id(user_id)

        teams_results, config = await asyncio.gather(teams_task, config_task)
        teams: list[Team] = [t for t in teams_results if t is not None]

        # Build list of content fetch tasks
        content_tasks = []
        content_keys = []

        # Org config
        content_tasks.append(self._content_repo.get_content(ORG_CONFIG_PATH))
        content_keys.append(("org", None))

        # Team configs
        for team in teams:
            path = self._get_team_config_path(team.id)
            content_tasks.append(self._content_repo.get_content(path))
            content_keys.append(("team", team.name))

        # User config (if exists)
        if config is not None:
            content_tasks.append(self._content_repo.get_content(config.git_path))
            content_keys.append(("user", None))

        # Fetch all content in parallel
        content_results = await asyncio.gather(*content_tasks)

        # Process results
        org_content = ""
        team_contents: list[tuple[str, str]] = []  # (team_name, content)
        user_content = ""

        for i, (key_type, key_name) in enumerate(content_keys):
            content = content_results[i] or ""
            if key_type == "org":
                org_content = content
            elif key_type == "team":
                if content:
                    team_contents.append((key_name, content))
            elif key_type == "user":
                user_content = content

        # Build merged content with section markers
        sections = []

        if org_content:
            sections.append(f"# Organization Configuration\n\n{org_content}")

        for team_name, content in team_contents:
            sections.append(f"# Team: {team_name}\n\n{content}")

        if user_content:
            sections.append(f"# Personal Configuration\n\n{user_content}")

        merged_content = "\n\n---\n\n".join(sections) if sections else ""

        # Combined team content for the breakdown field
        combined_team_content = "\n\n".join(content for _, content in team_contents)

        return EffectiveConfiguration(
            content=merged_content,
            org_content=org_content,
            team_content=combined_team_content,
            user_content=user_content,
        )
