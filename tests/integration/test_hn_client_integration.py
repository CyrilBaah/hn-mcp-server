"""Integration tests for HN client with real API."""

import pytest

from hn_mcp_server.models import Item, SearchResult, User
from hn_mcp_server.services import HNClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestHNClientIntegration:
    """Integration tests with real HN API."""

    async def test_real_search(self):
        """Test real search request."""
        async with HNClient() as client:
            result = await client.search(query="python", hits_per_page=5)

            assert isinstance(result, SearchResult)
            assert result.nb_hits > 0
            assert len(result.hits) > 0

    async def test_real_search_by_date(self):
        """Test real search by date request."""
        async with HNClient() as client:
            result = await client.search_by_date(tags=["story"], hits_per_page=5)

            assert isinstance(result, SearchResult)
            assert len(result.hits) > 0

            # Verify results are sorted by date (most recent first)
            timestamps = [hit.created_at_i for hit in result.hits]
            assert timestamps == sorted(timestamps, reverse=True)

    async def test_real_get_item(self):
        """Test real get item request."""
        # Use a well-known HN item ID (YC announcement)
        async with HNClient() as client:
            item = await client.get_item(1)

            assert isinstance(item, Item)
            assert item.id == 1

    async def test_real_get_user(self):
        """Test real get user request."""
        # Get pg's profile (Paul Graham, HN founder)
        async with HNClient() as client:
            user = await client.get_user("pg")

            assert isinstance(user, User)
            assert user.username == "pg"
            assert user.karma > 0

    async def test_front_page_stories(self):
        """Test getting front page stories."""
        async with HNClient() as client:
            result = await client.search(tags=["front_page"], hits_per_page=10)

            assert isinstance(result, SearchResult)
            assert len(result.hits) > 0

            # Verify all results are stories
            for hit in result.hits:
                assert "front_page" in hit.tags

    async def test_user_stories(self):
        """Test getting user's stories."""
        async with HNClient() as client:
            result = await client.search_by_date(
                tags=["story", "author_pg"],
                hits_per_page=5,
            )

            assert isinstance(result, SearchResult)

            # Verify all results are by the specified author
            for hit in result.hits:
                assert hit.author == "pg"

    async def test_time_range_search(self):
        """Test search with time range filter."""
        import time

        # Search for items from last 7 days
        now = int(time.time())
        week_ago = now - (7 * 24 * 60 * 60)

        async with HNClient() as client:
            result = await client.search_by_date(
                numeric_filters=[f"created_at_i>{week_ago}"],
                hits_per_page=10,
            )

            assert isinstance(result, SearchResult)
            assert len(result.hits) > 0

            # Verify all results are within time range
            for hit in result.hits:
                assert hit.created_at_i > week_ago

    async def test_high_points_filter(self):
        """Test filtering by minimum points."""
        async with HNClient() as client:
            result = await client.search(
                tags=["story"],
                numeric_filters=["points>500"],
                hits_per_page=10,
            )

            assert isinstance(result, SearchResult)

            # Verify all results have high points
            for hit in result.hits:
                if hit.points:
                    assert hit.points > 500
