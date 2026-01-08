"""HackerNews MCP Server.

A Model Context Protocol server that provides programmatic access to
HackerNews content through the official HN Algolia API.
"""

import asyncio
import logging
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tools import items, search, users

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("hn-mcp-server")

# Initialize MCP server
app = Server("hn-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="search_hn",
            description="Search HackerNews content by relevance (sorted by relevance, then points, then comments)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Full-text search query",
                        "default": "",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter tags (story, comment, poll, show_hn, ask_hn, front_page, author_USERNAME, story_ID)",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 0,
                        "minimum": 0,
                    },
                    "hits_per_page": {
                        "type": "integer",
                        "description": "Results per page (max: 1000)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                    "numeric_filters": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Numeric filters (e.g., 'points>100', 'created_at_i>1640000000')",
                    },
                },
            },
        ),
        Tool(
            name="search_hn_by_date",
            description="Search HackerNews content by date (sorted by most recent first)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Full-text search query",
                        "default": "",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter tags (story, comment, poll, show_hn, ask_hn, front_page, author_USERNAME, story_ID)",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 0,
                        "minimum": 0,
                    },
                    "hits_per_page": {
                        "type": "integer",
                        "description": "Results per page (max: 1000)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                    "numeric_filters": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Numeric filters (e.g., 'points>100', 'created_at_i>1640000000')",
                    },
                },
            },
        ),
        Tool(
            name="get_front_page",
            description="Retrieve current HackerNews front page stories",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 0,
                        "minimum": 0,
                    },
                    "hits_per_page": {
                        "type": "integer",
                        "description": "Results per page (max: 1000)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                },
            },
        ),
        Tool(
            name="get_latest_stories",
            description="Retrieve most recent HackerNews stories",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 0,
                        "minimum": 0,
                    },
                    "hits_per_page": {
                        "type": "integer",
                        "description": "Results per page (max: 1000)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                },
            },
        ),
        Tool(
            name="get_latest_comments",
            description="Retrieve most recent HackerNews comments",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 0,
                        "minimum": 0,
                    },
                    "hits_per_page": {
                        "type": "integer",
                        "description": "Results per page (max: 1000)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                },
            },
        ),
        Tool(
            name="search_by_time_range",
            description="Search HackerNews items within a specific time range",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_timestamp": {
                        "type": "integer",
                        "description": "Start time (Unix timestamp)",
                    },
                    "end_timestamp": {
                        "type": "integer",
                        "description": "End time (Unix timestamp)",
                    },
                    "query": {
                        "type": "string",
                        "description": "Full-text search query",
                        "default": "",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter tags",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 0,
                        "minimum": 0,
                    },
                    "hits_per_page": {
                        "type": "integer",
                        "description": "Results per page (max: 1000)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                },
                "required": ["start_timestamp", "end_timestamp"],
            },
        ),
        Tool(
            name="search_by_metrics",
            description="Search HackerNews items with minimum points or comments",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Full-text search query",
                        "default": "",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter tags",
                    },
                    "min_points": {
                        "type": "integer",
                        "description": "Minimum points threshold",
                        "minimum": 0,
                    },
                    "min_comments": {
                        "type": "integer",
                        "description": "Minimum number of comments threshold",
                        "minimum": 0,
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 0,
                        "minimum": 0,
                    },
                    "hits_per_page": {
                        "type": "integer",
                        "description": "Results per page (max: 1000)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                },
            },
        ),
        Tool(
            name="get_item",
            description="Retrieve a specific HackerNews item (story, comment, poll, etc.) by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "integer",
                        "description": "HackerNews item ID",
                    },
                },
                "required": ["item_id"],
            },
        ),
        Tool(
            name="get_story_comments",
            description="Retrieve a story and all its comments",
            inputSchema={
                "type": "object",
                "properties": {
                    "story_id": {
                        "type": "integer",
                        "description": "HackerNews story ID",
                    },
                },
                "required": ["story_id"],
            },
        ),
        Tool(
            name="get_user",
            description="Retrieve HackerNews user profile information",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "HackerNews username",
                    },
                },
                "required": ["username"],
            },
        ),
        Tool(
            name="get_user_stories",
            description="Retrieve all stories submitted by a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "HackerNews username",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 0,
                        "minimum": 0,
                    },
                    "hits_per_page": {
                        "type": "integer",
                        "description": "Results per page (max: 1000)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                },
                "required": ["username"],
            },
        ),
        Tool(
            name="get_user_comments",
            description="Retrieve all comments by a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "HackerNews username",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 0,
                        "minimum": 0,
                    },
                    "hits_per_page": {
                        "type": "integer",
                        "description": "Results per page (max: 1000)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                },
                "required": ["username"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Call an MCP tool."""
    try:
        # Route to appropriate tool
        if name == "search_hn":
            result = await search.search_hn(**arguments)
        elif name == "search_hn_by_date":
            result = await search.search_hn_by_date(**arguments)
        elif name == "get_front_page":
            result = await search.get_front_page(**arguments)
        elif name == "get_latest_stories":
            result = await search.get_latest_stories(**arguments)
        elif name == "get_latest_comments":
            result = await search.get_latest_comments(**arguments)
        elif name == "search_by_time_range":
            result = await search.search_by_time_range(**arguments)
        elif name == "search_by_metrics":
            result = await search.search_by_metrics(**arguments)
        elif name == "get_item":
            result = await items.get_item(**arguments)
        elif name == "get_story_comments":
            result = await items.get_story_comments(**arguments)
        elif name == "get_user":
            result = await users.get_user(**arguments)
        elif name == "get_user_stories":
            result = await users.get_user_stories(**arguments)
        elif name == "get_user_comments":
            result = await users.get_user_comments(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        import json

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {e!s}")]


async def main() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Starting HackerNews MCP Server")
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
