"""Atlas service - Main application service for catalog, configuration, and dashboard."""

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

import yaml
from pydantic import BaseModel

from atlas.adapters.catalog import AbstractCatalogRepository, VersionNotFoundError
from atlas.adapters.repository import AbstractRepository, EntityNotFoundError
from atlas.domain.entities import (
    CatalogItemType,
    ConfigurationVersion,
    EffectiveConfiguration,
    Team,
    UserConfiguration,
)


# -----------------------------------------------------------------------------
# Exceptions (application-level, wrapping adapter exceptions)
# -----------------------------------------------------------------------------


class ConfigurationNotFoundError(EntityNotFoundError):
    """Raised when configuration doesn't exist for user."""

    def __init__(self, user_id: UUID) -> None:
        super().__init__("Configuration", user_id)


class UserNotFoundError(EntityNotFoundError):
    """Raised when user doesn't exist."""

    def __init__(self, user_id: UUID) -> None:
        super().__init__("User", user_id)


# -----------------------------------------------------------------------------
# Scope enum for visibility
# -----------------------------------------------------------------------------


class CatalogScope(str, Enum):
    """Scope determines visibility of catalog items."""

    ORG = "org"  # Visible to everyone in the organization
    TEAM = "team"  # Visible only to team members
    USER = "user"  # Visible only to the specific user


# -----------------------------------------------------------------------------
# Data classes for catalog items
# -----------------------------------------------------------------------------


@dataclass
class CatalogItem:
    """Catalog item derived from git content."""

    id: str
    type: CatalogItemType
    name: str
    description: str
    git_path: str
    tags: list[str]
    scope: CatalogScope
    scope_id: Optional[UUID] = None  # team_id or user_id (None for org)
    readme_path: Optional[str] = None


@dataclass
class CatalogItemDetail(CatalogItem):
    """Catalog item with full documentation."""

    documentation: str = ""


# -----------------------------------------------------------------------------
# Pydantic models for dashboard
# -----------------------------------------------------------------------------


class TeamSummary(BaseModel):
    """Summary view of a team for dashboard display."""

    id: UUID
    name: str
    member_count: int


class CatalogItemSummary(BaseModel):
    """Summary view of a catalog item."""

    id: str
    type: CatalogItemType
    name: str
    description: str
    scope: CatalogScope
    scope_id: Optional[UUID] = None


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


# -----------------------------------------------------------------------------
# Main service
# -----------------------------------------------------------------------------


class AtlasService:
    """
    Main application service for Atlas.

    Handles:
    - Catalog: browsing skills, MCPs, tools from git (with visibility filtering)
    - Configuration: user/team/org config CRUD with git versioning
    - Dashboard: aggregated user data and effective config merging

    Repository structure:
    ```
    org/
        claude.md           # Org-wide config
        skills/             # Org-shared skills
        mcps/               # Org-shared MCPs
        tools/              # Org-shared tools
    teams/{team-uuid}/
        claude.md           # Team config
        skills/             # Team-only skills
        mcps/               # Team-only MCPs
        tools/              # Team-only tools
    users/{user-uuid}/
        claude.md           # User config
        skills/             # User-only skills
        mcps/               # User-only MCPs
        tools/              # User-only tools
    ```
    """

    ITEM_TYPES: dict[str, CatalogItemType] = {
        "skills": CatalogItemType.SKILL,
        "mcps": CatalogItemType.MCP,
        "tools": CatalogItemType.TOOL,
    }

    CACHE_TTL_SECONDS = 300  # 5 minutes

    def __init__(
        self,
        repo: AbstractRepository,
        catalog_repo: AbstractCatalogRepository,
    ) -> None:
        self._repo = repo
        self._catalog_repo = catalog_repo
        self._cache: list[CatalogItem] = []
        self._cache_time: Optional[datetime] = None

    # -------------------------------------------------------------------------
    # Catalog: Read items from git with scope-based visibility
    # -------------------------------------------------------------------------

    def _generate_catalog_id(self, git_path: str) -> str:
        """Generate stable ID from git path."""
        return hashlib.sha256(git_path.encode()).hexdigest()[:16]

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self._cache_time:
            return False
        return datetime.utcnow() - self._cache_time < timedelta(
            seconds=self.CACHE_TTL_SECONDS
        )

    async def _parse_catalog_item_metadata(
        self,
        item_path: str,
        item_type: CatalogItemType,
        scope: CatalogScope,
        scope_id: Optional[UUID] = None,
    ) -> Optional[CatalogItem]:
        """Parse metadata from item's config.yaml or derive from path."""
        config_path = f"{item_path}/config.yaml"
        readme_path = f"{item_path}/README.md"

        # Extract name from path (last component)
        name = item_path.rsplit("/", 1)[-1]
        description = ""
        tags: list[str] = []

        config_content = await self._catalog_repo.get_content(config_path)
        if config_content:
            try:
                config = yaml.safe_load(config_content)
                if isinstance(config, dict):
                    name = config.get("name", name)
                    description = config.get("description", "")
                    tags = config.get("tags", [])
                    if isinstance(tags, str):
                        tags = [t.strip() for t in tags.split(",")]
            except yaml.YAMLError:
                pass

        return CatalogItem(
            id=self._generate_catalog_id(item_path),
            type=item_type,
            name=name,
            description=description,
            git_path=item_path,
            tags=tags,
            scope=scope,
            scope_id=scope_id,
            readme_path=readme_path,
        )

    async def _load_items_from_scope(
        self,
        base_path: str,
        scope: CatalogScope,
        scope_id: Optional[UUID] = None,
    ) -> list[CatalogItem]:
        """Load all catalog items from a specific scope directory."""
        items: list[CatalogItem] = []

        for type_dir, item_type in self.ITEM_TYPES.items():
            search_path = f"{base_path}/{type_dir}/"
            try:
                paths = await self._catalog_repo.list_contents(search_path)
            except Exception:
                continue

            # Extract unique item directories
            item_dirs: set[str] = set()
            for path in paths:
                # path is like "org/skills/my-skill/config.yaml"
                # We want "org/skills/my-skill"
                parts = path.split("/")
                # Find the index of type_dir and take one more
                try:
                    type_idx = parts.index(type_dir)
                    if len(parts) > type_idx + 1:
                        item_dirs.add("/".join(parts[: type_idx + 2]))
                except ValueError:
                    continue

            for item_path in item_dirs:
                item = await self._parse_catalog_item_metadata(
                    item_path, item_type, scope, scope_id
                )
                if item:
                    items.append(item)

        return items

    async def _load_all_catalog_items(self) -> list[CatalogItem]:
        """Load all catalog items from all scopes (org, teams, users)."""
        items: list[CatalogItem] = []

        # Load org-level items
        org_items = await self._load_items_from_scope("org", CatalogScope.ORG)
        items.extend(org_items)

        # Load team-level items
        try:
            team_paths = await self._catalog_repo.list_contents("teams/")
            team_ids: set[str] = set()
            for path in team_paths:
                parts = path.split("/")
                if len(parts) >= 2:
                    team_ids.add(parts[1])

            for team_id_str in team_ids:
                try:
                    team_id = UUID(team_id_str)
                    team_items = await self._load_items_from_scope(
                        f"teams/{team_id_str}", CatalogScope.TEAM, team_id
                    )
                    items.extend(team_items)
                except ValueError:
                    continue
        except Exception:
            pass

        # Load user-level items
        try:
            user_paths = await self._catalog_repo.list_contents("users/")
            user_ids: set[str] = set()
            for path in user_paths:
                parts = path.split("/")
                if len(parts) >= 2:
                    user_ids.add(parts[1])

            for user_id_str in user_ids:
                try:
                    user_id = UUID(user_id_str)
                    user_items = await self._load_items_from_scope(
                        f"users/{user_id_str}", CatalogScope.USER, user_id
                    )
                    items.extend(user_items)
                except ValueError:
                    continue
        except Exception:
            pass

        return items

    def _filter_items_by_visibility(
        self,
        items: list[CatalogItem],
        user_id: Optional[UUID],
        team_ids: list[UUID],
    ) -> list[CatalogItem]:
        """Filter catalog items based on user's visibility."""
        visible_items: list[CatalogItem] = []

        for item in items:
            if item.scope == CatalogScope.ORG:
                # Org items visible to everyone
                visible_items.append(item)
            elif item.scope == CatalogScope.TEAM:
                # Team items visible only to team members
                if item.scope_id in team_ids:
                    visible_items.append(item)
            elif item.scope == CatalogScope.USER:
                # User items visible only to that user
                if item.scope_id == user_id:
                    visible_items.append(item)

        return visible_items

    async def _ensure_cache(self) -> list[CatalogItem]:
        """Ensure cache is loaded and valid."""
        if not self._is_cache_valid():
            await self.refresh_catalog_cache()
        return self._cache

    async def refresh_catalog_cache(self) -> None:
        """Force refresh the catalog cache."""
        self._cache = await self._load_all_catalog_items()
        self._cache_time = datetime.utcnow()

    async def list_catalog_items(
        self,
        user_id: Optional[UUID] = None,
        team_ids: Optional[list[UUID]] = None,
        item_type: Optional[CatalogItemType] = None,
        search_query: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[CatalogItem], int]:
        """
        List catalog items with visibility filtering and pagination.

        Args:
            user_id: Current user's ID for visibility filtering
            team_ids: User's team IDs for visibility filtering
            item_type: Filter by item type
            search_query: Search in name, description, tags
            offset: Pagination offset
            limit: Pagination limit

        Returns (items, total_count).
        """
        all_items = await self._ensure_cache()

        # Apply visibility filter
        if user_id is not None:
            items = self._filter_items_by_visibility(
                all_items, user_id, team_ids or []
            )
        else:
            # No user context - only show org items
            items = [i for i in all_items if i.scope == CatalogScope.ORG]

        # Apply type filter
        if item_type:
            items = [i for i in items if i.type == item_type]

        # Apply search filter
        if search_query:
            query = search_query.lower()
            items = [
                i
                for i in items
                if query in i.name.lower()
                or query in i.description.lower()
                or any(query in tag.lower() for tag in i.tags)
            ]

        # Sort and paginate
        items = sorted(items, key=lambda i: i.name.lower())
        total = len(items)
        paginated = items[offset : offset + limit]

        return paginated, total

    async def get_catalog_item(
        self,
        item_id: str,
        user_id: Optional[UUID] = None,
        team_ids: Optional[list[UUID]] = None,
    ) -> Optional[CatalogItemDetail]:
        """
        Get a single catalog item with full documentation.

        Checks visibility before returning.
        """
        all_items = await self._ensure_cache()

        item = next((i for i in all_items if i.id == item_id), None)
        if not item:
            return None

        # Check visibility
        if user_id is not None:
            visible_items = self._filter_items_by_visibility(
                [item], user_id, team_ids or []
            )
            if not visible_items:
                return None  # User doesn't have access

        documentation = ""
        if item.readme_path:
            content = await self._catalog_repo.get_content(item.readme_path)
            if content:
                documentation = content

        return CatalogItemDetail(
            id=item.id,
            type=item.type,
            name=item.name,
            description=item.description,
            git_path=item.git_path,
            tags=item.tags,
            scope=item.scope,
            scope_id=item.scope_id,
            readme_path=item.readme_path,
            documentation=documentation,
        )

    async def count_catalog_items_by_type(
        self,
        user_id: Optional[UUID] = None,
        team_ids: Optional[list[UUID]] = None,
    ) -> dict[CatalogItemType, int]:
        """Count catalog items by type with visibility filtering."""
        all_items = await self._ensure_cache()

        if user_id is not None:
            items = self._filter_items_by_visibility(
                all_items, user_id, team_ids or []
            )
        else:
            items = [i for i in all_items if i.scope == CatalogScope.ORG]

        counts = {t: 0 for t in CatalogItemType}
        for item in items:
            counts[item.type] += 1
        return counts

    # -------------------------------------------------------------------------
    # Catalog: Create/Update/Delete items in user's namespace
    # -------------------------------------------------------------------------

    def _get_user_catalog_path(
        self, user_id: UUID, item_type: CatalogItemType, name: str
    ) -> str:
        """Get git path for user's catalog item."""
        type_dir = {
            CatalogItemType.SKILL: "skills",
            CatalogItemType.MCP: "mcps",
            CatalogItemType.TOOL: "tools",
        }[item_type]
        return f"users/{user_id}/{type_dir}/{name}"

    async def create_catalog_item(
        self,
        user_id: UUID,
        item_type: CatalogItemType,
        name: str,
        description: str,
        tags: list[str],
        content: str,
    ) -> CatalogItemDetail:
        """
        Create a new catalog item in user's namespace.

        Creates config.yaml and README.md in git.
        """
        # Validate name (alphanumeric, hyphens, underscores only)
        import re
        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            raise ValueError("Name must contain only letters, numbers, hyphens, and underscores")

        base_path = self._get_user_catalog_path(user_id, item_type, name)

        # Check if already exists
        if await self._catalog_repo.exists(f"{base_path}/README.md"):
            raise ValueError(f"Item '{name}' already exists")

        # Create config.yaml
        config_yaml = f"name: {name}\ndescription: {description}\ntags: [{', '.join(tags)}]\n"
        await self._catalog_repo.save_content(
            path=f"{base_path}/config.yaml",
            content=config_yaml,
            message=f"Create {item_type.value} {name}: config.yaml",
        )

        # Create README.md
        await self._catalog_repo.save_content(
            path=f"{base_path}/README.md",
            content=content,
            message=f"Create {item_type.value} {name}: README.md",
        )

        # Refresh cache to include new item
        await self.refresh_catalog_cache()

        # Return the created item
        item_id = self._generate_catalog_id(base_path)
        return CatalogItemDetail(
            id=item_id,
            type=item_type,
            name=name,
            description=description,
            git_path=base_path,
            tags=tags,
            scope=CatalogScope.USER,
            scope_id=user_id,
            readme_path=f"{base_path}/README.md",
            documentation=content,
        )

    async def update_catalog_item(
        self,
        user_id: UUID,
        item_id: str,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        content: Optional[str] = None,
    ) -> Optional[CatalogItemDetail]:
        """
        Update an existing catalog item.

        Only the owner can update their items.
        """
        # Find the item
        all_items = await self._ensure_cache()
        item = next((i for i in all_items if i.id == item_id), None)

        if item is None:
            return None

        # Check ownership
        if item.scope != CatalogScope.USER or item.scope_id != user_id:
            return None

        # Update config.yaml if description or tags changed
        if description is not None or tags is not None:
            new_desc = description if description is not None else item.description
            new_tags = tags if tags is not None else item.tags
            config_yaml = f"name: {item.name}\ndescription: {new_desc}\ntags: [{', '.join(new_tags)}]\n"
            await self._catalog_repo.save_content(
                path=f"{item.git_path}/config.yaml",
                content=config_yaml,
                message=f"Update {item.type.value} {item.name}: config.yaml",
            )

        # Update README.md if content changed
        if content is not None:
            await self._catalog_repo.save_content(
                path=f"{item.git_path}/README.md",
                content=content,
                message=f"Update {item.type.value} {item.name}: README.md",
            )

        # Refresh cache
        await self.refresh_catalog_cache()

        # Return updated item
        return CatalogItemDetail(
            id=item.id,
            type=item.type,
            name=item.name,
            description=description if description is not None else item.description,
            git_path=item.git_path,
            tags=tags if tags is not None else item.tags,
            scope=item.scope,
            scope_id=item.scope_id,
            readme_path=item.readme_path,
            documentation=content if content is not None else (
                await self._catalog_repo.get_content(item.readme_path) or ""
            ),
        )

    async def delete_catalog_item(
        self,
        user_id: UUID,
        item_id: str,
    ) -> bool:
        """
        Delete a catalog item.

        Only the owner can delete their items.
        Returns True if deleted, False if not found or not authorized.
        """
        # Find the item
        all_items = await self._ensure_cache()
        item = next((i for i in all_items if i.id == item_id), None)

        if item is None:
            return False

        # Check ownership
        if item.scope != CatalogScope.USER or item.scope_id != user_id:
            return False

        # Delete files
        try:
            await self._catalog_repo.delete_content(
                path=f"{item.git_path}/README.md",
                message=f"Delete {item.type.value} {item.name}: README.md",
            )
        except Exception:
            pass

        try:
            await self._catalog_repo.delete_content(
                path=f"{item.git_path}/config.yaml",
                message=f"Delete {item.type.value} {item.name}: config.yaml",
            )
        except Exception:
            pass

        # Refresh cache
        await self.refresh_catalog_cache()

        return True

    # -------------------------------------------------------------------------
    # Configuration: User/Team/Org config CRUD with git versioning
    # -------------------------------------------------------------------------

    def _get_org_config_path(self) -> str:
        """Get git path for org configuration."""
        return "org/claude.md"

    def _get_team_config_path(self, team_id: UUID) -> str:
        """Get git path for team's configuration."""
        return f"teams/{team_id}/claude.md"

    def _get_user_config_path(self, user_id: UUID) -> str:
        """Get git path for user's configuration."""
        return f"users/{user_id}/claude.md"

    async def get_user_configuration(
        self, user_id: UUID
    ) -> tuple[str, UserConfiguration]:
        """
        Get user's current configuration content and metadata.

        Returns tuple of (content, metadata).
        Returns empty content if user has no configuration yet.
        """
        config = await self._repo.get_configuration_by_user_id(user_id)

        if config is None:
            path = self._get_user_config_path(user_id)
            return "", UserConfiguration(
                id=uuid4(),
                user_id=user_id,
                git_path=path,
                current_commit_sha="",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

        content = await self._catalog_repo.get_content(config.git_path)
        return content or "", config

    async def save_user_configuration(
        self,
        user_id: UUID,
        content: str,
        message: Optional[str] = None,
    ) -> UserConfiguration:
        """
        Save configuration content with git versioning.

        Creates or updates the configuration, committing to git and
        updating database metadata.
        """
        path = self._get_user_config_path(user_id)
        commit_message = message or f"Update configuration for user {user_id}"

        commit_sha = await self._catalog_repo.save_content(
            path=path,
            content=content,
            message=commit_message,
        )

        config = await self._repo.get_configuration_by_user_id(user_id)
        if config is None:
            config = UserConfiguration(
                id=uuid4(),
                user_id=user_id,
                git_path=path,
                current_commit_sha=commit_sha,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        else:
            config = UserConfiguration(
                id=config.id,
                user_id=config.user_id,
                git_path=config.git_path,
                current_commit_sha=commit_sha,
                created_at=config.created_at,
                updated_at=datetime.utcnow(),
            )

        return await self._repo.save_configuration(config)

    async def get_configuration_versions(
        self,
        user_id: UUID,
        limit: int = 50,
    ) -> list[ConfigurationVersion]:
        """
        Get version history for user's configuration.

        Returns empty list if no configuration exists yet.
        """
        config = await self._repo.get_configuration_by_user_id(user_id)
        if config is None:
            return []

        return await self._catalog_repo.get_version_history(
            path=config.git_path,
            limit=limit,
        )

    async def rollback_configuration_to_version(
        self,
        user_id: UUID,
        commit_sha: str,
    ) -> UserConfiguration:
        """
        Rollback configuration to a previous version.

        Gets content from historical commit and saves as new commit.
        """
        config = await self._repo.get_configuration_by_user_id(user_id)
        if config is None:
            raise ConfigurationNotFoundError(user_id)

        old_content = await self._catalog_repo.get_content_at_version(
            path=config.git_path,
            commit_sha=commit_sha,
        )
        if old_content is None:
            raise VersionNotFoundError(commit_sha, config.git_path)

        return await self.save_user_configuration(
            user_id=user_id,
            content=old_content,
            message=f"Rollback to version {commit_sha[:7]}",
        )

    async def import_user_configuration(
        self,
        user_id: UUID,
        content: str,
    ) -> UserConfiguration:
        """
        Import configuration from uploaded file content.

        Same as save_user_configuration but with different commit message.
        """
        return await self.save_user_configuration(
            user_id=user_id,
            content=content,
            message="Import configuration from local file",
        )

    async def get_effective_configuration(
        self, user_id: UUID
    ) -> EffectiveConfiguration:
        """
        Get merged configuration from org -> team -> user levels.

        Fetches configuration content from all levels and merges with section markers.
        """
        user = await self._repo.get_user_by_id(user_id)
        if user is None:
            return EffectiveConfiguration(
                content="", org_content="", team_content="", user_content=""
            )

        teams_task = asyncio.gather(
            *[self._repo.get_team_by_id(tid) for tid in user.team_ids]
        )
        config_task = self._repo.get_configuration_by_user_id(user_id)

        teams_results, config = await asyncio.gather(teams_task, config_task)
        teams: list[Team] = [t for t in teams_results if t is not None]

        content_tasks = []
        content_keys = []

        # Org config
        content_tasks.append(self._catalog_repo.get_content(self._get_org_config_path()))
        content_keys.append(("org", None))

        # Team configs
        for team in teams:
            path = self._get_team_config_path(team.id)
            content_tasks.append(self._catalog_repo.get_content(path))
            content_keys.append(("team", team.name))

        # User config
        if config is not None:
            content_tasks.append(self._catalog_repo.get_content(config.git_path))
            content_keys.append(("user", None))

        content_results = await asyncio.gather(*content_tasks)

        org_content = ""
        team_contents: list[tuple[str, str]] = []
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

        sections = []

        if org_content:
            sections.append(f"# Organization Configuration\n\n{org_content}")

        for team_name, content in team_contents:
            sections.append(f"# Team: {team_name}\n\n{content}")

        if user_content:
            sections.append(f"# Personal Configuration\n\n{user_content}")

        merged_content = "\n\n---\n\n".join(sections) if sections else ""
        combined_team_content = "\n\n".join(content for _, content in team_contents)

        return EffectiveConfiguration(
            content=merged_content,
            org_content=org_content,
            team_content=combined_team_content,
            user_content=user_content,
        )

    # -------------------------------------------------------------------------
    # Dashboard: Aggregated user data
    # -------------------------------------------------------------------------

    async def get_dashboard(self, user_id: UUID) -> UserDashboard:
        """
        Get aggregated dashboard data for a user.

        Fetches user info, teams, available item counts, and config status.
        """
        user = await self._repo.get_user_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)

        teams_task = asyncio.gather(
            *[self._repo.get_team_by_id(tid) for tid in user.team_ids]
        )
        counts_task = self.count_catalog_items_by_type(user_id, user.team_ids)
        config_task = self._repo.get_configuration_by_user_id(user_id)

        teams_results, counts, config = await asyncio.gather(
            teams_task, counts_task, config_task
        )

        teams: list[Team] = [t for t in teams_results if t is not None]

        team_summaries = [
            TeamSummary(id=team.id, name=team.name, member_count=team.member_count)
            for team in teams
        ]

        return UserDashboard(
            user_id=user.id,
            username=user.username,
            email=user.email,
            teams=team_summaries,
            available_skills=counts.get(CatalogItemType.SKILL, 0),
            available_mcps=counts.get(CatalogItemType.MCP, 0),
            available_tools=counts.get(CatalogItemType.TOOL, 0),
            has_configuration=config is not None,
            configuration_updated_at=config.updated_at if config else None,
        )

    async def get_available_items(
        self,
        user_id: UUID,
        item_type: Optional[CatalogItemType] = None,
    ) -> list[CatalogItemSummary]:
        """
        Get catalog items available to a user based on their visibility.

        Returns items from:
        - org/* (everyone)
        - teams/{user's-teams}/* (team members)
        - users/{user}/* (that user only)
        """
        user = await self._repo.get_user_by_id(user_id)
        team_ids = user.team_ids if user else []

        items, _ = await self.list_catalog_items(
            user_id=user_id,
            team_ids=team_ids,
            item_type=item_type,
        )

        return [
            CatalogItemSummary(
                id=item.id,
                type=item.type,
                name=item.name,
                description=item.description,
                scope=item.scope,
                scope_id=item.scope_id,
            )
            for item in items
        ]
