"""Item-related MCP tools for HackerNews."""

from typing import Any

from ..services import HNClient


async def get_item(item_id: int) -> dict[str, Any]:
    """Retrieve a specific HackerNews item by ID.

    Gets a story, comment, poll, or other item including all nested children (comments).

    Args:
        item_id: HackerNews item ID

    Returns:
        Complete item with nested children

    Raises:
        HNClientError: On API errors
    """
    async with HNClient() as client:
        item = await client.get_item(item_id)
        return item.model_dump(mode='json', by_alias=True)


async def get_story_comments(story_id: int) -> dict[str, Any]:
    """Retrieve a story and all its comments.

    Args:
        story_id: HackerNews story ID

    Returns:
        Story with full comment tree

    Raises:
        HNClientError: On API errors
    """
    async with HNClient() as client:
        story = await client.get_item(story_id)

        # Verify it's a story
        if not story.is_story:
            raise ValueError(f"Item {story_id} is not a story")

        return story.model_dump(mode='json', by_alias=True)
