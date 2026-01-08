"""HackerNews API client service."""

import asyncio
from typing import Any

import httpx
from pydantic import ValidationError

from ..models import Item, SearchResult, User
from ..models.errors import APIErrorResponse, ErrorDetails


class HNClientError(Exception):
    """Base exception for HN client errors."""

    def __init__(self, error_response: APIErrorResponse) -> None:
        self.error_response = error_response
        super().__init__(error_response.error.message)


class HNClient:
    """Async HTTP client for HackerNews Algolia API."""

    def __init__(
        self,
        base_url: str = "https://hn.algolia.com/api/v1",
        timeout: float = 10.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize HN API client.

        Args:
            base_url: Base URL for HN API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "HNClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        retry_count: int = 0,
    ) -> dict[str, Any]:
        """Make an HTTP request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            retry_count: Current retry attempt number

        Returns:
            JSON response data

        Raises:
            HNClientError: On API or network errors
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        try:
            response = await self._client.request(method, endpoint, params=params)
            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException as e:
            if retry_count < self.max_retries:
                await asyncio.sleep(2**retry_count)  # Exponential backoff
                return await self._request(method, endpoint, params, retry_count + 1)

            raise HNClientError(
                APIErrorResponse(
                    error=ErrorDetails(
                        code="TIMEOUT",
                        message=f"Request timed out after {self.timeout}s",
                        details={"endpoint": endpoint},
                    )
                )
            ) from e

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HNClientError(
                    APIErrorResponse(
                        error=ErrorDetails(
                            code="NOT_FOUND",
                            message="Resource not found",
                            details={"endpoint": endpoint, "status_code": 404},
                        )
                    )
                ) from e

            if e.response.status_code == 429:
                raise HNClientError(
                    APIErrorResponse(
                        error=ErrorDetails(
                            code="RATE_LIMIT_EXCEEDED",
                            message="API rate limit exceeded",
                            details={
                                "endpoint": endpoint,
                                "status_code": 429,
                                "retry_after": e.response.headers.get("Retry-After"),
                            },
                        )
                    )
                ) from e

            raise HNClientError(
                APIErrorResponse(
                    error=ErrorDetails(
                        code="API_ERROR",
                        message=f"API error: {e.response.status_code}",
                        details={"endpoint": endpoint, "status_code": e.response.status_code},
                    )
                )
            ) from e

        except httpx.RequestError as e:
            raise HNClientError(
                APIErrorResponse(
                    error=ErrorDetails(
                        code="NETWORK_ERROR",
                        message=f"Network error: {e!s}",
                        details={"endpoint": endpoint},
                    )
                )
            ) from e

    async def search(
        self,
        query: str = "",
        tags: list[str] | None = None,
        numeric_filters: list[str] | None = None,
        page: int = 0,
        hits_per_page: int = 20,
    ) -> SearchResult:
        """Search HackerNews by relevance.

        Args:
            query: Search query
            tags: Filter tags
            numeric_filters: Numeric filters
            page: Page number
            hits_per_page: Results per page

        Returns:
            SearchResult object

        Raises:
            HNClientError: On API errors
        """
        params: dict[str, Any] = {
            "query": query,
            "page": page,
            "hitsPerPage": hits_per_page,
        }

        if tags:
            params["tags"] = ",".join(tags)
        if numeric_filters:
            params["numericFilters"] = ",".join(numeric_filters)

        try:
            data = await self._request("GET", "/search", params)
            return SearchResult.model_validate(data)
        except ValidationError as e:
            raise HNClientError(
                APIErrorResponse(
                    error=ErrorDetails(
                        code="API_ERROR",
                        message="Failed to parse search response",
                        details={"validation_errors": str(e)},
                    )
                )
            ) from e

    async def search_by_date(
        self,
        query: str = "",
        tags: list[str] | None = None,
        numeric_filters: list[str] | None = None,
        page: int = 0,
        hits_per_page: int = 20,
    ) -> SearchResult:
        """Search HackerNews by date.

        Args:
            query: Search query
            tags: Filter tags
            numeric_filters: Numeric filters
            page: Page number
            hits_per_page: Results per page

        Returns:
            SearchResult object

        Raises:
            HNClientError: On API errors
        """
        params: dict[str, Any] = {
            "query": query,
            "page": page,
            "hitsPerPage": hits_per_page,
        }

        if tags:
            params["tags"] = ",".join(tags)
        if numeric_filters:
            params["numericFilters"] = ",".join(numeric_filters)

        try:
            data = await self._request("GET", "/search_by_date", params)
            return SearchResult.model_validate(data)
        except ValidationError as e:
            raise HNClientError(
                APIErrorResponse(
                    error=ErrorDetails(
                        code="API_ERROR",
                        message="Failed to parse search response",
                        details={"validation_errors": str(e)},
                    )
                )
            ) from e

    async def get_item(self, item_id: int) -> Item:
        """Get item by ID.

        Args:
            item_id: Item ID

        Returns:
            Item object

        Raises:
            HNClientError: On API errors
        """
        try:
            data = await self._request("GET", f"/items/{item_id}")
            return Item.model_validate(data)
        except ValidationError as e:
            raise HNClientError(
                APIErrorResponse(
                    error=ErrorDetails(
                        code="API_ERROR",
                        message="Failed to parse item response",
                        details={"validation_errors": str(e), "item_id": item_id},
                    )
                )
            ) from e

    async def get_user(self, username: str) -> User:
        """Get user by username.

        Args:
            username: HackerNews username

        Returns:
            User object

        Raises:
            HNClientError: On API errors
        """
        try:
            data = await self._request("GET", f"/users/{username}")
            return User.model_validate(data)
        except ValidationError as e:
            raise HNClientError(
                APIErrorResponse(
                    error=ErrorDetails(
                        code="API_ERROR",
                        message="Failed to parse user response",
                        details={"validation_errors": str(e), "username": username},
                    )
                )
            ) from e
