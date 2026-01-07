# HackerNews MCP Server Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Reference](#api-reference)
4. [Data Models](#data-models)
5. [Integration Guide](#integration-guide)
6. [Advanced Usage](#advanced-usage)
7. [Performance & Optimization](#performance--optimization)

## Overview

The HackerNews MCP Server provides a Model Context Protocol interface to the HackerNews Algolia API. It enables AI assistants and other applications to search and retrieve HackerNews content programmatically.

### Key Features

- **Async/Await**: Built on asyncio for high performance
- **Type Safety**: Full type hints with MyPy strict mode
- **Data Validation**: Pydantic models ensure data integrity
- **Error Handling**: Comprehensive error handling and logging
- **Stdio Transport**: MCP stdio protocol for easy integration

## Architecture

### Components

```
┌─────────────────────────────────────────┐
│         MCP Client (Claude, etc.)       │
└─────────────────┬───────────────────────┘
                  │ stdio
                  │
┌─────────────────▼───────────────────────┐
│          MCP Server (server.py)         │
│  ┌────────────────────────────────┐    │
│  │   Tool Handlers                │    │
│  │   - search_hn                  │    │
│  │   - search_hn_by_date          │    │
│  │   - get_item                   │    │
│  │   - get_user                   │    │
│  └────────────┬───────────────────┘    │
└───────────────┼────────────────────────┘
                │
┌───────────────▼────────────────────────┐
│      HN API Client (hn_client.py)      │
│  ┌────────────────────────────────┐   │
│  │   httpx AsyncClient            │   │
│  │   - Connection pooling         │   │
│  │   - Timeout handling           │   │
│  │   - Response parsing           │   │
│  └────────────┬───────────────────┘   │
└───────────────┼────────────────────────┘
                │ HTTPS
                │
┌───────────────▼────────────────────────┐
│      HackerNews Algolia API            │
│      https://hn.algolia.com/api/v1/    │
└────────────────────────────────────────┘
```

### File Organization

- **server.py**: MCP server initialization and tool registration
- **services/hn_client.py**: HTTP client for HN API
- **models/**: Pydantic data models
  - `search.py`: Search results and hits
  - `item.py`: Items with nested children
  - `user.py`: User profiles
- **tools/**: MCP tool implementations (modular design)

## API Reference

### Search Tools

#### search_hn

Search HackerNews by relevance.

```python
async def search_hn(
    query: str = "",
    tags: list[str] | None = None,
    page: int = 0,
    hits_per_page: int = 20,
    numeric_filters: list[str] | None = None,
) -> SearchResult
```

**Available Tags:**
- `story`: Top-level stories
- `comment`: Comments on stories
- `poll`: Polls
- `pollopt`: Poll options
- `show_hn`: Show HN posts
- `ask_hn`: Ask HN posts
- `front_page`: Front page stories
- `author_USERNAME`: Posts by specific user
- `story_ID`: Comments on specific story

**Numeric Filters:**
- `created_at_i>TIMESTAMP`: Items created after timestamp
- `created_at_i<TIMESTAMP`: Items created before timestamp
- `points>N`: Items with more than N points
- `points<N`: Items with less than N points
- `num_comments>N`: Items with more than N comments

**Example:**
```json
{
  "query": "python machine learning",
  "tags": ["story", "show_hn"],
  "numeric_filters": ["points>100", "created_at_i>1609459200"],
  "hits_per_page": 30
}
```

#### search_hn_by_date

Same as `search_hn` but sorted by date (most recent first).

### Item Tools

#### get_item

Retrieve a specific item with all nested children.

```python
async def get_item(item_id: int) -> Item
```

**Returns:**
- Full item object
- Nested children (comments)
- All metadata fields

**Example:**
```json
{
  "item_id": 39251790
}
```

### User Tools

#### get_user

Retrieve user profile.

```python
async def get_user(username: str) -> User
```

**Example:**
```json
{
  "username": "pg"
}
```

## Data Models

### SearchResult

```python
class SearchResult(BaseModel):
    hits: list[Hit]
    page: int
    nb_hits: int
    nb_pages: int
    hits_per_page: int
    processing_time_ms: int
    query: str
    params: str
```

### Hit

```python
class Hit(BaseModel):
    object_id: str
    created_at: datetime
    created_at_i: int
    author: str
    
    # Story fields
    title: str | None
    url: HttpUrl | None
    points: int | None
    num_comments: int
    story_text: str | None
    
    # Comment fields
    comment_text: str | None
    parent_id: int | None
    story_id: int | None
    
    # Metadata
    tags: list[str]
    highlight_result: dict[str, Any]
```

### Item

```python
class Item(BaseModel):
    id: int
    created_at: datetime
    author: str | None
    type: str | None
    
    title: str | None
    url: HttpUrl | None
    text: str | None
    points: int | None
    parent_id: int | None
    story_id: int | None
    
    children: list["Item"]  # Recursive
```

**Helper Methods:**
- `is_story()`: Check if item is a story
- `is_comment()`: Check if item is a comment
- `flatten_comments()`: Get all comments as flat list
- `total_comments()`: Count total nested comments

### User

```python
class User(BaseModel):
    username: str
    about: str | None
    karma: int
    created: str | None
    created_at: str | None
```

## Integration Guide

### Claude Desktop Integration

1. **Find Config File:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add Server Configuration:**
```json
{
  "mcpServers": {
    "hackernews": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "hn_mcp_server.server"]
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Test Connection:**
   - Ask: "Search HackerNews for Python stories"
   - Claude should use the `search_hn` tool

### Custom MCP Client Integration

```python
import asyncio
from mcp.client import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "hn_mcp_server.server"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            
            # Call a tool
            result = await session.call_tool(
                "search_hn",
                arguments={"query": "python", "tags": ["story"]}
            )
            print(result)

asyncio.run(main())
```

## Advanced Usage

### Complex Search Queries

**Find trending Show HN posts:**
```json
{
  "query": "",
  "tags": ["show_hn"],
  "numeric_filters": ["points>50", "num_comments>10"],
  "hits_per_page": 20
}
```

**Search specific user's posts:**
```json
{
  "tags": ["author_pg", "story"],
  "hits_per_page": 50
}
```

**Time-based search:**
```json
{
  "query": "AI",
  "numeric_filters": ["created_at_i>1704067200"],  // After Jan 1, 2024
  "hits_per_page": 100
}
```

### Working with Nested Comments

```python
# Get story with comments
item = await hn_client.get_item(39251790)

# Access nested structure
print(f"Story: {item.title}")
print(f"Direct replies: {len(item.children)}")
print(f"Total comments: {item.total_comments()}")

# Flatten all comments
all_comments = item.flatten_comments()
for comment in all_comments:
    print(f"{comment.author}: {comment.text}")
```

### Pagination

```python
# Get multiple pages
async def get_all_results(query: str, max_pages: int = 5):
    results = []
    for page in range(max_pages):
        result = await hn_client.search(
            query=query,
            page=page,
            hits_per_page=100
        )
        results.extend(result.hits)
        if page >= result.nb_pages - 1:
            break
    return results
```

## Performance & Optimization

### Connection Pooling

The `HNClient` uses httpx's built-in connection pooling:
- Reuses connections across requests
- Reduces latency for subsequent calls
- Automatic connection cleanup

### Rate Limiting

HN API limits: 10,000 requests/hour per IP

Best practices:
- Cache results when possible
- Use appropriate `hits_per_page` values
- Implement exponential backoff for retries

### Memory Usage

- Models use `exclude_none=True` to reduce JSON size
- Connection pool limits prevent memory bloat
- Async operations prevent blocking

### Timeout Configuration

Default timeout: 30 seconds

Adjust in `hn_client.py`:
```python
self.client = httpx.AsyncClient(
    base_url=self.BASE_URL,
    timeout=60.0,  # Increase for slow connections
)
```

### Error Handling

The server handles:
- Network errors (retries with backoff)
- Invalid responses (validation errors)
- Rate limiting (429 status codes)
- Timeout errors

All errors are logged and returned to the client with descriptive messages.

## Logging

Configure logging level:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,  # or INFO, WARNING, ERROR
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```

Log locations:
- Server events: `hn_mcp_server.server`
- API calls: `hn_mcp_server.services.hn_client`
- Tool calls: `hn_mcp_server.tools.*`

## Troubleshooting

### Common Issues

**Import Errors:**
- Ensure virtual environment is activated
- Verify installation: `pip list | grep hn-mcp-server`

**Connection Refused:**
- Check HN API status: https://hn.algolia.com/api
- Verify internet connection
- Check firewall settings

**Invalid Responses:**
- Enable DEBUG logging to see raw responses
- Verify item IDs exist on HackerNews
- Check username spelling

**Performance Issues:**
- Reduce `hits_per_page`
- Implement result caching
- Use more specific queries

## Support & Resources

- **MCP Protocol**: https://modelcontextprotocol.io/
- **HN API Docs**: https://hn.algolia.com/api
- **httpx Docs**: https://www.python-httpx.org/
- **Pydantic Docs**: https://docs.pydantic.dev/
