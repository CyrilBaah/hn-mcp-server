"""User-related MCP tools for HackerNews."""

from typing import Any

from ..services import HNClient


async def get_user(username: str) -> dict[str, Any]:
    """Retrieve HackerNews user profile information.

    Args:
        username: HackerNews username

    Returns:
        User profile with username, about, karma

    Raises:
        HNClientError: On API errors
    """
    async with HNClient() as client:
        user = await client.get_user(username)
        return user.model_dump(mode='json', by_alias=True)


async def get_user_stories(
    username: str,
    page: int = 0,
    hits_per_page: int = 20,
) -> dict[str, Any]:
    """Retrieve all stories submitted by a user.

    Args:
        username: HackerNews username
        page: Page number for pagination (default: 0)
        hits_per_page: Results per page (default: 20, max: 1000)

    Returns:
        User's stories sorted by date

    Raises:
        HNClientError: On API errors
    """
    async with HNClient() as client:
        result = await client.search_by_date(
            tags=["story", f"author_{username}"],
            page=page,
            hits_per_page=hits_per_page,
        )
        return result.model_dump(mode='json', by_alias=True)


async def get_user_comments(
    username: str,
    page: int = 0,
    hits_per_page: int = 20,
) -> dict[str, Any]:
    """Retrieve all comments by a user.

    Args:
        username: HackerNews username
        page: Page number for pagination (default: 0)
        hits_per_page: Results per page (default: 20, max: 1000)

    Returns:
        User's comments sorted by date

    Raises:
        HNClientError: On API errors
    """
    async with HNClient() as client:
        result = await client.search_by_date(
            tags=["comment", f"author_{username}"],
            page=page,
            hits_per_page=hits_per_page,
        )
        return result.model_dump(mode='json', by_alias=True)
