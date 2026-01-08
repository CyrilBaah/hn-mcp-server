"""Search-related MCP tools for HackerNews."""

from typing import Any

from ..services import HNClient


async def search_hn(
    query: str = "",
    tags: list[str] | None = None,
    page: int = 0,
    hits_per_page: int = 20,
    numeric_filters: list[str] | None = None,
) -> dict[str, Any]:
    """Search HackerNews content by relevance.

    Searches HackerNews stories, comments, and other content sorted by relevance,
    then points, then number of comments.

    Args:
        query: Full-text search query
        tags: Filter by tags (story, comment, poll, show_hn, ask_hn, front_page, author_USERNAME, story_ID)
        page: Page number for pagination (default: 0)
        hits_per_page: Results per page (default: 20, max: 1000)
        numeric_filters: Numeric filters (e.g., ["points>100", "created_at_i>1640000000"])

    Returns:
        Search results with hits, pagination metadata, and processing time

    Raises:
        HNClientError: On API errors
    """
    async with HNClient() as client:
        result = await client.search(
            query=query,
            tags=tags,
            numeric_filters=numeric_filters,
            page=page,
            hits_per_page=hits_per_page,
        )
        return result.model_dump(mode='json', by_alias=True)


async def search_hn_by_date(
    query: str = "",
    tags: list[str] | None = None,
    page: int = 0,
    hits_per_page: int = 20,
    numeric_filters: list[str] | None = None,
) -> dict[str, Any]:
    """Search HackerNews content by date.

    Searches HackerNews stories, comments, and other content sorted by date (most recent first).

    Args:
        query: Full-text search query
        tags: Filter by tags (story, comment, poll, show_hn, ask_hn, front_page, author_USERNAME, story_ID)
        page: Page number for pagination (default: 0)
        hits_per_page: Results per page (default: 20, max: 1000)
        numeric_filters: Numeric filters (e.g., ["points>100", "created_at_i>1640000000"])

    Returns:
        Search results with hits, pagination metadata, and processing time

    Raises:
        HNClientError: On API errors
    """
    async with HNClient() as client:
        result = await client.search_by_date(
            query=query,
            tags=tags,
            numeric_filters=numeric_filters,
            page=page,
            hits_per_page=hits_per_page,
        )
        return result.model_dump(mode='json', by_alias=True)


async def get_front_page(
    page: int = 0,
    hits_per_page: int = 20,
) -> dict[str, Any]:
    """Retrieve current HackerNews front page stories.

    Args:
        page: Page number for pagination (default: 0)
        hits_per_page: Results per page (default: 20, max: 1000)

    Returns:
        Front page stories with metadata

    Raises:
        HNClientError: On API errors
    """
    async with HNClient() as client:
        result = await client.search(
            tags=["front_page"],
            page=page,
            hits_per_page=hits_per_page,
        )
        return result.model_dump(mode='json', by_alias=True)


async def get_latest_stories(
    page: int = 0,
    hits_per_page: int = 20,
) -> dict[str, Any]:
    """Retrieve most recent HackerNews stories.

    Args:
        page: Page number for pagination (default: 0)
        hits_per_page: Results per page (default: 20, max: 1000)

    Returns:
        Latest stories sorted by creation date

    Raises:
        HNClientError: On API errors
    """
    async with HNClient() as client:
        result = await client.search_by_date(
            tags=["story"],
            page=page,
            hits_per_page=hits_per_page,
        )
        return result.model_dump(mode='json', by_alias=True)


async def get_latest_comments(
    page: int = 0,
    hits_per_page: int = 20,
) -> dict[str, Any]:
    """Retrieve most recent HackerNews comments.

    Args:
        page: Page number for pagination (default: 0)
        hits_per_page: Results per page (default: 20, max: 1000)

    Returns:
        Latest comments sorted by creation date

    Raises:
        HNClientError: On API errors
    """
    async with HNClient() as client:
        result = await client.search_by_date(
            tags=["comment"],
            page=page,
            hits_per_page=hits_per_page,
        )
        return result.model_dump(mode='json', by_alias=True)


async def search_by_time_range(
    start_timestamp: int,
    end_timestamp: int,
    query: str = "",
    tags: list[str] | None = None,
    page: int = 0,
    hits_per_page: int = 20,
) -> dict[str, Any]:
    """Search HackerNews items within a specific time range.

    Args:
        start_timestamp: Start time (Unix timestamp)
        end_timestamp: End time (Unix timestamp)
        query: Full-text search query
        tags: Filter by tags
        page: Page number for pagination (default: 0)
        hits_per_page: Results per page (default: 20, max: 1000)

    Returns:
        Search results filtered by time range

    Raises:
        HNClientError: On API errors
        ValueError: If end_timestamp < start_timestamp
    """
    if end_timestamp < start_timestamp:
        raise ValueError("end_timestamp must be greater than or equal to start_timestamp")

    numeric_filters = [
        f"created_at_i>={start_timestamp}",
        f"created_at_i<={end_timestamp}",
    ]

    async with HNClient() as client:
        result = await client.search_by_date(
            query=query,
            tags=tags,
            numeric_filters=numeric_filters,
            page=page,
            hits_per_page=hits_per_page,
        )
        return result.model_dump(mode='json', by_alias=True)


async def search_by_metrics(
    query: str = "",
    tags: list[str] | None = None,
    min_points: int | None = None,
    min_comments: int | None = None,
    page: int = 0,
    hits_per_page: int = 20,
) -> dict[str, Any]:
    """Search HackerNews items with minimum points or comments.

    Args:
        query: Full-text search query
        tags: Filter by tags
        min_points: Minimum points threshold
        min_comments: Minimum number of comments threshold
        page: Page number for pagination (default: 0)
        hits_per_page: Results per page (default: 20, max: 1000)

    Returns:
        Search results filtered by metrics

    Raises:
        HNClientError: On API errors
    """
    numeric_filters = []

    if min_points is not None:
        numeric_filters.append(f"points>={min_points}")
    if min_comments is not None:
        numeric_filters.append(f"num_comments>={min_comments}")

    async with HNClient() as client:
        result = await client.search(
            query=query,
            tags=tags,
            numeric_filters=numeric_filters if numeric_filters else None,
            page=page,
            hits_per_page=hits_per_page,
        )
        return result.model_dump(mode='json', by_alias=True)
