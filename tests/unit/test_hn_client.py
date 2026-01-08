"""Unit tests for HN client."""

import pytest
from pytest_httpx import HTTPXMock

from hn_mcp_server.models import Item, SearchResult, User
from hn_mcp_server.services import HNClient, HNClientError


@pytest.mark.asyncio
class TestHNClient:
    """Test HNClient class."""

    async def test_search_success(self, httpx_mock: HTTPXMock, sample_search_response):
        """Test successful search request."""
        httpx_mock.add_response(
            url="https://hn.algolia.com/api/v1/search?query=python&page=0&hitsPerPage=20",
            json=sample_search_response,
        )

        async with HNClient() as client:
            result = await client.search(query="python")

            assert isinstance(result, SearchResult)
            assert result.query == "test"
            assert len(result.hits) == 1

    async def test_search_with_filters(self, httpx_mock: HTTPXMock, sample_search_response):
        """Test search with tags and filters."""
        httpx_mock.add_response(json=sample_search_response)

        async with HNClient() as client:
            result = await client.search(
                query="python",
                tags=["story"],
                numeric_filters=["points>100"],
                hits_per_page=50,
            )

            assert isinstance(result, SearchResult)

        # Verify request was made with correct params
        request = httpx_mock.get_request()
        assert "tags=story" in str(request.url)
        assert "numericFilters=points%3E100" in str(request.url)

    async def test_search_by_date(self, httpx_mock: HTTPXMock, sample_search_response):
        """Test search by date."""
        httpx_mock.add_response(
            url="https://hn.algolia.com/api/v1/search_by_date?query=python&page=0&hitsPerPage=20",
            json=sample_search_response,
        )

        async with HNClient() as client:
            result = await client.search_by_date(query="python")

            assert isinstance(result, SearchResult)

    async def test_get_item_success(self, httpx_mock: HTTPXMock, sample_item_response):
        """Test successful get item request."""
        httpx_mock.add_response(
            url="https://hn.algolia.com/api/v1/items/1",
            json=sample_item_response,
        )

        async with HNClient() as client:
            item = await client.get_item(1)

            assert isinstance(item, Item)
            assert item.id == 1
            assert item.author == "testuser"

    async def test_get_user_success(self, httpx_mock: HTTPXMock, sample_user_response):
        """Test successful get user request."""
        httpx_mock.add_response(
            url="https://hn.algolia.com/api/v1/users/testuser",
            json=sample_user_response,
        )

        async with HNClient() as client:
            user = await client.get_user("testuser")

            assert isinstance(user, User)
            assert user.username == "testuser"
            assert user.karma == 5000

    async def test_not_found_error(self, httpx_mock: HTTPXMock):
        """Test 404 error handling."""
        httpx_mock.add_response(
            url="https://hn.algolia.com/api/v1/items/999999",
            status_code=404,
        )

        async with HNClient() as client:
            with pytest.raises(HNClientError) as exc_info:
                await client.get_item(999999)

            assert exc_info.value.error_response.error.code == "NOT_FOUND"

    async def test_rate_limit_error(self, httpx_mock: HTTPXMock):
        """Test 429 rate limit error handling."""
        httpx_mock.add_response(
            status_code=429,
            headers={"Retry-After": "60"},
        )

        async with HNClient() as client:
            with pytest.raises(HNClientError) as exc_info:
                await client.search(query="test")

            error = exc_info.value.error_response.error
            assert error.code == "RATE_LIMIT_EXCEEDED"
            assert error.details["retry_after"] == "60"

    async def test_timeout_with_retry(self, httpx_mock: HTTPXMock):
        """Test timeout with retry logic."""
        import httpx
        # First 2 requests timeout, 3rd succeeds
        httpx_mock.add_exception(httpx.TimeoutException("Timeout"))
        httpx_mock.add_exception(httpx.TimeoutException("Timeout"))
        httpx_mock.add_response(json={"hits": [], "page": 0, "nbHits": 0, "nbPages": 0, "hitsPerPage": 20, "processingTimeMS": 1, "query": "", "params": ""})

        async with HNClient(max_retries=3) as client:
            result = await client.search()
            assert isinstance(result, SearchResult)

    async def test_max_retries_exceeded(self, httpx_mock: HTTPXMock):
        """Test max retries exceeded."""
        import httpx
        # All requests timeout (1 initial + 2 retries = 3 total attempts)
        for _ in range(3):
            httpx_mock.add_exception(httpx.TimeoutException("Timeout"))

        async with HNClient(max_retries=2, timeout=0.1) as client:
            with pytest.raises(HNClientError):
                await client.search()

    async def test_context_manager(self, httpx_mock: HTTPXMock, sample_search_response):
        """Test async context manager."""
        httpx_mock.add_response(json=sample_search_response)

        async with HNClient() as client:
            assert client._client is not None
            await client.search()

        # Client should be closed after exiting context
        assert client._client is None

    async def test_custom_base_url(self, httpx_mock: HTTPXMock, sample_search_response):
        """Test custom base URL."""
        custom_url = "https://custom.api.com/v1"

        httpx_mock.add_response(
            url=f"{custom_url}/search?query=test&page=0&hitsPerPage=20",
            json=sample_search_response,
        )

        async with HNClient(base_url=custom_url) as client:
            await client.search(query="test")
