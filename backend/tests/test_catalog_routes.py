"""Tests for catalog service methods."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from atlas.domain.entities.catalog_item import CatalogItemType
from atlas.application.services.atlas_service import AtlasService, CatalogScope, CatalogItem, CatalogItemDetail


@pytest.fixture
def mock_repo():
    """Create mock repository."""
    return AsyncMock()


@pytest.fixture
def mock_catalog_repo():
    """Create mock catalog repository."""
    repo = AsyncMock()
    repo.exists.return_value = False
    repo.save_content.return_value = "abc123commit"
    repo.get_content.return_value = "# Test content"
    repo.delete_content.return_value = "def456commit"
    repo.list_contents.return_value = []
    return repo


@pytest.fixture
def atlas_service(mock_repo, mock_catalog_repo):
    """Create AtlasService with mocked dependencies."""
    return AtlasService(repo=mock_repo, catalog_repo=mock_catalog_repo)


class TestCatalogItemCreate:
    """Tests for create_catalog_item method."""

    @pytest.mark.asyncio
    async def test_create_item_success(self, atlas_service, mock_catalog_repo):
        """Creating an item saves config.yaml and README.md."""
        user_id = uuid4()

        result = await atlas_service.create_catalog_item(
            user_id=user_id,
            item_type=CatalogItemType.SKILL,
            name="test-skill",
            description="A test skill",
            tags=["test", "example"],
            content="# Test Skill\n\nDocumentation here.",
        )

        assert result.name == "test-skill"
        assert result.type == CatalogItemType.SKILL
        assert result.description == "A test skill"
        assert result.scope == CatalogScope.USER
        assert result.scope_id == user_id

        # Verify save_content was called for config.yaml and README.md
        assert mock_catalog_repo.save_content.call_count == 2

    @pytest.mark.asyncio
    async def test_create_item_validates_name(self, atlas_service):
        """Creating an item with invalid name raises ValueError."""
        user_id = uuid4()

        with pytest.raises(ValueError) as exc_info:
            await atlas_service.create_catalog_item(
                user_id=user_id,
                item_type=CatalogItemType.SKILL,
                name="invalid name!",  # Contains space and special char
                description="Invalid",
                tags=[],
                content="# Test",
            )

        assert "Name must contain only letters" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_item_checks_exists(self, atlas_service, mock_catalog_repo):
        """Creating an item that exists raises ValueError."""
        user_id = uuid4()
        mock_catalog_repo.exists.return_value = True

        with pytest.raises(ValueError) as exc_info:
            await atlas_service.create_catalog_item(
                user_id=user_id,
                item_type=CatalogItemType.SKILL,
                name="existing-skill",
                description="Already exists",
                tags=[],
                content="# Test",
            )

        assert "already exists" in str(exc_info.value)


class TestCatalogItemUpdate:
    """Tests for update_catalog_item method."""

    @pytest.mark.asyncio
    async def test_update_item_not_found(self, atlas_service):
        """Updating non-existent item returns None."""
        user_id = uuid4()

        result = await atlas_service.update_catalog_item(
            user_id=user_id,
            item_id="nonexistent",
            description="New description",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_update_item_wrong_owner(self, atlas_service):
        """Updating item owned by another user returns None."""
        from datetime import datetime
        user_id = uuid4()
        other_user_id = uuid4()

        # Add a cached item owned by other user
        atlas_service._cache = [
            CatalogItem(
                id="item123",
                type=CatalogItemType.SKILL,
                name="test-skill",
                description="Test",
                git_path=f"users/{other_user_id}/skills/test-skill",
                tags=[],
                scope=CatalogScope.USER,
                scope_id=other_user_id,
            )
        ]
        atlas_service._cache_time = datetime.utcnow()  # Set valid cache time

        result = await atlas_service.update_catalog_item(
            user_id=user_id,  # Different user
            item_id="item123",
            description="New description",
        )

        assert result is None


class TestCatalogItemDelete:
    """Tests for delete_catalog_item method."""

    @pytest.mark.asyncio
    async def test_delete_item_not_found(self, atlas_service):
        """Deleting non-existent item returns False."""
        user_id = uuid4()

        result = await atlas_service.delete_catalog_item(
            user_id=user_id,
            item_id="nonexistent",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_item_wrong_owner(self, atlas_service):
        """Deleting item owned by another user returns False."""
        from datetime import datetime
        user_id = uuid4()
        other_user_id = uuid4()

        atlas_service._cache = [
            CatalogItem(
                id="item123",
                type=CatalogItemType.SKILL,
                name="test-skill",
                description="Test",
                git_path=f"users/{other_user_id}/skills/test-skill",
                tags=[],
                scope=CatalogScope.USER,
                scope_id=other_user_id,
            )
        ]
        atlas_service._cache_time = datetime.utcnow()

        result = await atlas_service.delete_catalog_item(
            user_id=user_id,
            item_id="item123",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_item_success(self, atlas_service, mock_catalog_repo):
        """Deleting owned item calls delete_content and returns True."""
        from datetime import datetime
        user_id = uuid4()

        atlas_service._cache = [
            CatalogItem(
                id="item123",
                type=CatalogItemType.SKILL,
                name="test-skill",
                description="Test",
                git_path=f"users/{user_id}/skills/test-skill",
                tags=[],
                scope=CatalogScope.USER,
                scope_id=user_id,
            )
        ]
        atlas_service._cache_time = datetime.utcnow()  # Set valid cache time

        result = await atlas_service.delete_catalog_item(
            user_id=user_id,
            item_id="item123",
        )

        assert result is True
        # Verify delete was called for README.md and config.yaml
        assert mock_catalog_repo.delete_content.call_count == 2


class TestCatalogPaths:
    """Tests for catalog path generation."""

    def test_user_catalog_path_skill(self, atlas_service):
        """User skill path is correct."""
        user_id = uuid4()
        path = atlas_service._get_user_catalog_path(user_id, CatalogItemType.SKILL, "my-skill")
        assert path == f"users/{user_id}/skills/my-skill"

    def test_user_catalog_path_mcp(self, atlas_service):
        """User MCP path is correct."""
        user_id = uuid4()
        path = atlas_service._get_user_catalog_path(user_id, CatalogItemType.MCP, "my-mcp")
        assert path == f"users/{user_id}/mcps/my-mcp"

    def test_user_catalog_path_tool(self, atlas_service):
        """User tool path is correct."""
        user_id = uuid4()
        path = atlas_service._get_user_catalog_path(user_id, CatalogItemType.TOOL, "my-tool")
        assert path == f"users/{user_id}/tools/my-tool"
