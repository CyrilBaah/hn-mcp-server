# Quick Start Guide: HackerNews MCP Server

**Version**: 1.0.0  
**Last Updated**: 2025-01-05

## Overview

The HackerNews MCP Server provides AI assistants and MCP clients with programmatic access to HackerNews content through the official Algolia API. Search stories, retrieve comments, explore user profiles, and more.

## Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- MCP-compatible client (Claude Desktop, Continue, etc.)

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install hn-mcp-server
```

### Option 2: Install from Source

```bash
# Clone repository
git clone https://github.com/CyrilBaah/hn-mcp-server.git
cd hn-mcp-server

# Install with pip
pip install -e .

# Or with uv (faster)
uv pip install -e .
```

### Option 3: Install via MCP Client

Many MCP clients can install servers directly. Check your client's documentation.

## Configuration

### Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hackernews": {
      "command": "python",
      "args": ["-m", "hn_mcp_server"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Other MCP Clients

Consult your MCP client documentation. The server uses stdio transport and requires:
- **Command**: `python -m hn_mcp_server`
- **Transport**: stdio

## Environment Variables

Optional configuration via environment variables:

```bash
# API configuration
export HN_API_BASE_URL="https://hn.algolia.com/api/v1"  # Default
export HN_REQUEST_TIMEOUT="10"  # Seconds, default: 10
export HN_MAX_RETRIES="3"  # Default: 3

# Logging
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

## Available Tools

### Search Tools

#### `search_hn`
Search HackerNews content by relevance.

```python
# Example usage in MCP client
search_hn(
    query="artificial intelligence",
    tags=["story"],
    hits_per_page=20
)
```

**Parameters**:
- `query` (string, required): Search query
- `tags` (string[], optional): Filter tags
- `page` (int, optional): Page number
- `hits_per_page` (int, optional): Results per page (max 1000)
- `numeric_filters` (string[], optional): Numeric filters

#### `search_hn_by_date`
Search HackerNews content by date (most recent first).

```python
search_hn_by_date(
    query="python",
    tags=["story"],
    page=0
)
```

#### `get_front_page`
Get current HackerNews front page stories.

```python
get_front_page(hits_per_page=30)
```

#### `get_latest_stories`
Get the most recent stories.

```python
get_latest_stories(hits_per_page=50)
```

#### `get_latest_comments`
Get the most recent comments.

```python
get_latest_comments(hits_per_page=50)
```

### Item Tools

#### `get_item`
Retrieve a specific item by ID.

```python
get_item(item_id=12345678)
```

**Returns**: Complete item with nested children (comments)

#### `get_story_comments`
Get a story with all its comments.

```python
get_story_comments(story_id=12345678)
```

### User Tools

#### `get_user`
Get user profile information.

```python
get_user(username="pg")
```

**Returns**: Username, about, karma

#### `get_user_stories`
Get all stories by a user.

```python
get_user_stories(
    username="pg",
    page=0,
    hits_per_page=20
)
```

#### `get_user_comments`
Get all comments by a user.

```python
get_user_comments(
    username="pg",
    page=0,
    hits_per_page=20
)
```

### Advanced Filter Tools

#### `search_by_time_range`
Search within a specific time range.

```python
search_by_time_range(
    start_timestamp=1609459200,  # Unix timestamp
    end_timestamp=1640995200,
    tags=["story"],
    query="startup"
)
```

#### `search_by_metrics`
Filter by minimum points or comments.

```python
search_by_metrics(
    min_points=100,
    min_comments=50,
    query="AI",
    tags=["story"]
)
```

## Common Usage Patterns

### Find Trending Topics

```python
# Get high-engagement recent stories
search_by_metrics(
    min_points=100,
    min_comments=20,
    tags=["story"]
)
```

### Monitor Specific Author

```python
# Get latest posts from specific user
get_user_stories(username="dang", hits_per_page=10)
```

### Research Time Period

```python
# Stories from 2024
search_by_time_range(
    start_timestamp=1704067200,  # Jan 1, 2024
    end_timestamp=1735689600,    # Dec 31, 2024
    tags=["story"],
    query="machine learning"
)
```

### Track Discussion

```python
# Get story and all comments
story = get_story_comments(story_id=39251790)
print(f"Story: {story['title']}")
print(f"Comments: {len(story['children'])}")
```

## Tag Reference

### Content Types
- `story` - Regular stories
- `comment` - Comments
- `poll` - Polls
- `pollopt` - Poll options
- `show_hn` - Show HN posts
- `ask_hn` - Ask HN posts

### Special Tags
- `front_page` - Currently on front page
- `author_USERNAME` - Posts by specific author
- `story_ID` - Comments on specific story

### Tag Combinations
Tags are ANDed by default. Use parentheses for OR:

```python
# Stories OR polls by pg
search_hn(tags=["author_pg", "(story,poll)"])

# Show HN that are currently on front page
search_hn(tags=["show_hn", "front_page"])
```

## Numeric Filters

### Available Fields
- `created_at_i` - Unix timestamp
- `points` - Story points
- `num_comments` - Comment count

### Operators
- `<` - Less than
- `<=` - Less than or equal
- `=` - Equal
- `>` - Greater than
- `>=` - Greater than or equal

### Examples

```python
# Stories with at least 100 points
search_hn(
    tags=["story"],
    numeric_filters=["points>=100"]
)

# Comments in the last 24 hours
import time
yesterday = int(time.time()) - 86400
search_hn_by_date(
    tags=["comment"],
    numeric_filters=[f"created_at_i>{yesterday}"]
)

# Highly discussed stories
search_hn(
    tags=["story"],
    numeric_filters=["points>50", "num_comments>20"]
)
```

## Error Handling

The server returns structured errors:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit reached. Try again later.",
    "details": {
      "retry_after": 3600
    }
  }
}
```

### Error Codes
- `INVALID_PARAMETER` - Invalid input
- `RATE_LIMIT_EXCEEDED` - Hit API rate limit
- `API_ERROR` - HN API error
- `NETWORK_ERROR` - Network issue
- `NOT_FOUND` - Item/user not found
- `TIMEOUT` - Request timed out

## Performance Tips

1. **Pagination**: Use `hits_per_page` to control result size (max 1000)
2. **Rate Limits**: Server enforces 10,000 requests/hour limit
3. **Specific Queries**: Use tags and filters to narrow results
4. **Caching**: Consider caching results client-side for repeated queries

## Troubleshooting

### Server Won't Start

**Problem**: `ModuleNotFoundError: No module named 'hn_mcp_server'`

**Solution**: Ensure package is installed:
```bash
pip install hn-mcp-server
# or
pip install -e .
```

### Rate Limit Errors

**Problem**: Frequent `RATE_LIMIT_EXCEEDED` errors

**Solution**: The server respects HN API's 10,000 requests/hour limit. Space out requests or reduce query frequency.

### Slow Responses

**Problem**: Queries taking > 2 seconds

**Solution**: 
- Reduce `hits_per_page` (fewer results = faster)
- Use more specific queries and filters
- Check network connectivity

### No Results

**Problem**: Search returns empty results

**Solution**:
- Verify query spelling
- Try broader search terms
- Check tag combinations (tags are ANDed)
- Ensure numeric filters aren't too restrictive

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=hn_mcp_server --cov-report=html

# Run specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/
```

### Code Quality

```bash
# Linting and formatting
ruff check .
ruff format .

# Type checking
mypy src/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## Support

- **Issues**: https://github.com/yourusername/hn-mcp-server/issues
- **Documentation**: https://context7.io/hn-mcp-server
- **MCP Spec**: https://spec.modelcontextprotocol.io

## License

MIT License - See LICENSE file for details
