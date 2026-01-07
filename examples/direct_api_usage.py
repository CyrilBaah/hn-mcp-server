"""Example: Direct API usage without MCP."""

import asyncio

from hn_mcp_server.services import HNClient


async def main():
    """Demonstrate HackerNews API client usage."""
    print("HackerNews API Client - Example Usage\n")

    async with HNClient() as client:
        # Example 1: Search for Python stories
        print("=" * 60)
        print("Example 1: Search for Python stories")
        print("=" * 60)

        result = await client.search(query="python", tags=["story"], hits_per_page=5)

        print(f"\nFound {result.nb_hits} results (showing {len(result.hits)}):\n")

        for hit in result.hits:
            print(f"  • {hit.title}")
            print(f"    Points: {hit.points} | Comments: {hit.num_comments}")
            print(f"    Author: {hit.author}")
            print(f"    URL: {hit.url}\n")

        # Example 2: Get front page stories
        print("=" * 60)
        print("Example 2: Front page stories")
        print("=" * 60)

        result = await client.search(tags=["front_page"], hits_per_page=10)

        print(f"\nCurrent front page ({len(result.hits)} stories):\n")

        for i, hit in enumerate(result.hits, 1):
            print(f"  {i}. {hit.title}")
            print(f"     {hit.points} points by {hit.author}\n")

        # Example 3: Get latest comments
        print("=" * 60)
        print("Example 3: Latest comments")
        print("=" * 60)

        result = await client.search_by_date(tags=["comment"], hits_per_page=5)

        print(f"\nLatest {len(result.hits)} comments:\n")

        for hit in result.hits:
            comment_preview = (hit.comment_text or "")[:100]
            print(f"  • {hit.author}: {comment_preview}...")
            print(f"    Story ID: {hit.story_id}\n")

        # Example 4: Get user profile
        print("=" * 60)
        print("Example 4: User profile (pg)")
        print("=" * 60)

        user = await client.get_user("pg")

        print(f"\nUsername: {user.username}")
        print(f"Karma: {user.karma:,}")
        if user.about:
            print(f"About: {user.about[:200]}...")

        # Example 5: Get specific item
        print("\n" + "=" * 60)
        print("Example 5: Get specific item (HN item #1)")
        print("=" * 60)

        item = await client.get_item(1)

        print(f"\nID: {item.id}")
        print(f"Author: {item.author}")
        print(f"Type: {item.type}")
        if item.title:
            print(f"Title: {item.title}")
        if item.url:
            print(f"URL: {item.url}")
        print(f"Comments: {item.total_comments()}")


if __name__ == "__main__":
    asyncio.run(main())
