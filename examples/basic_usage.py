"""Example: Using the HN MCP server with a custom client."""

import asyncio
import sys

from mcp.client import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Example of using HN MCP server programmatically."""

    # Configure server connection
    server_params = StdioServerParameters(
        command=sys.executable,  # Use current Python interpreter
        args=["-m", "hn_mcp_server"],
    )

    # Connect to server
    async with (
        stdio_client(server_params) as (read, write),
        ClientSession(read, write) as session,
    ):
        # Initialize session
        await session.initialize()

        # List available tools
        tools_response = await session.list_tools()
        print(f"Available tools: {[t.name for t in tools_response.tools]}")
        print()

        # Example 1: Search for Python stories
        print("Example 1: Search for Python stories")
        result = await session.call_tool(
            "search_hn",
            arguments={
                "query": "python",
                "tags": ["story"],
                "hits_per_page": 5
            }
        )
        print(result.content[0].text[:500])  # First 500 chars
        print()

        # Example 2: Get front page
        print("Example 2: Get front page stories")
        result = await session.call_tool(
            "search_hn",
            arguments={
                "tags": ["front_page"],
                "hits_per_page": 5
            }
        )
        print(result.content[0].text[:500])
        print()

        # Example 3: Get specific item
        print("Example 3: Get specific item")
        result = await session.call_tool(
            "get_item",
            arguments={"item_id": 1}
        )
        print(result.content[0].text[:500])
        print()

        # Example 4: Get user profile
        print("Example 4: Get user profile")
        result = await session.call_tool(
            "get_user",
            arguments={"username": "pg"}
        )
        print(result.content[0].text)
        print()


if __name__ == "__main__":
    asyncio.run(main())
