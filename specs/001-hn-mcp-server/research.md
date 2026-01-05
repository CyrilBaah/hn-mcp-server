# Research: HackerNews MCP Server

**Phase**: 0 - Technical Research  
**Date**: 2025-01-05  
**Status**: Complete

## Executive Summary

Research confirms the HackerNews MCP Server is feasible using the official MCP Python SDK, HN Algolia API, and modern Python tooling. All technical requirements can be met with existing packages, avoiding custom implementations per constitution principles.

## HackerNews API Analysis

### API Endpoints

#### 1. Search API
**Base URL**: `https://hn.algolia.com/api/v1`

**Search by Relevance**
- Endpoint: `GET /search?query={query}`
- Sorting: Relevance → Points → Comments
- Pagination: `page`, `hitsPerPage` (max 1000)
- Filters: `tags`, `numericFilters`

**Search by Date**
- Endpoint: `GET /search_by_date?query={query}`
- Sorting: Date (newest first)
- Same parameters as relevance search

**Available Tags**:
- Type: `story`, `comment`, `poll`, `pollopt`
- Special: `show_hn`, `ask_hn`, `front_page`
- Author: `author_USERNAME`
- Story reference: `story_ID`

**Numeric Filters**:
- `created_at_i` (Unix timestamp)
- `points` (story points)
- `num_comments` (comment count)
- Operators: `<`, `<=`, `=`, `>`, `>=`

**Example Queries**:
```
# Front page stories
/search?tags=front_page

# Latest stories
/search_by_date?tags=story

# Stories by pg
/search?tags=story,author_pg

# Stories in time range
/search_by_date?tags=story&numericFilters=created_at_i>1609459200,created_at_i<1640995200

# High-engagement posts
/search?tags=story&numericFilters=points>100,num_comments>50
```

#### 2. Items API
**Endpoint**: `GET /items/{id}`

Returns full item with nested children:
```json
{
  "id": 1,
  "created_at": "2006-10-09T18:21:51.000Z",
  "author": "pg",
  "title": "Y Combinator",
  "url": "http://ycombinator.com/",
  "text": null,
  "points": 57,
  "parent_id": null,
  "children": [...]
}
```

#### 3. Users API
**Endpoint**: `GET /users/{username}`

Returns user profile:
```json
{
  "username": "pg",
  "about": "Founder of YC...",
  "karma": 155111
}
```

### Rate Limits
- **Limit**: 10,000 requests per hour per IP
- **Recommended**: Implement request tracking and throttling
- **Strategy**: Client-side rate limiting to stay under quota

### Performance Characteristics
- Response time: ~50-200ms (observed)
- Data freshness: Near real-time (< 1 minute delay)
- Availability: 99.9%+ uptime

## Model Context Protocol (MCP) Research

### MCP Python SDK
**Package**: `mcp` (official Anthropic/ModelContext SDK)
**Latest Version**: 1.1.0 (as of Jan 2025)
**Repository**: https://github.com/modelcontextprotocol/python-sdk

### Key Components

#### 1. Server Setup
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("hn-mcp-server")

@app.tool()
async def search_hn(query: str, tags: list[str] | None = None) -> dict:
    """Search HackerNews content"""
    # Implementation
    pass
```

#### 2. Tool Decorator
- Automatic schema generation from type hints
- Built-in parameter validation
- Async/await support

#### 3. Transport
- stdio transport (standard for MCP)
- Server communicates via stdin/stdout
- JSON-RPC protocol

### Sample Implementation Pattern
```python
from mcp.server import Server
from mcp.types import Tool, TextContent
import httpx

app = Server("hn-mcp-server")

@app.tool()
async def get_item(item_id: int) -> dict:
    """
    Retrieve a HackerNews item by ID.
    
    Args:
        item_id: The HackerNews item ID
        
    Returns:
        Item data with nested children
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://hn.algolia.com/api/v1/items/{item_id}"
        )
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    asyncio.run(stdio_server(app))
```

## Technical Stack Validation

### HTTP Client: httpx
**Why httpx over requests**:
- Native async/await support (required for MCP)
- HTTP/2 support
- Connection pooling
- Timeout management
- Better error handling

**Version**: 0.27.0+ (latest stable)

**Example Usage**:
```python
import httpx

async def fetch_data(url: str, params: dict) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
```

### Data Validation: Pydantic v2
**Why Pydantic**:
- Automatic validation from type hints
- JSON serialization/deserialization
- Error messages for invalid data
- Integration with FastAPI/MCP patterns

**Version**: 2.10.0+ (latest stable)

**Example Models**:
```python
from pydantic import BaseModel, Field
from datetime import datetime

class HNItem(BaseModel):
    id: int
    created_at: datetime
    author: str
    title: str | None = None
    url: str | None = None
    text: str | None = None
    points: int | None = None
    parent_id: int | None = None
    children: list['HNItem'] = Field(default_factory=list)

class SearchResult(BaseModel):
    hits: list[dict]
    page: int
    nb_hits: int = Field(alias="nbHits")
    nb_pages: int = Field(alias="nbPages")
    hits_per_page: int = Field(alias="hitsPerPage")
    processing_time_ms: int = Field(alias="processingTimeMS")
    query: str
    params: str
```

### Testing: pytest + pytest-asyncio
**Packages**:
- `pytest` 8.3.0+ - Testing framework
- `pytest-asyncio` 0.24.0+ - Async test support
- `pytest-cov` 6.0.0+ - Coverage reporting
- `pytest-httpx` 0.30.0+ - Mock httpx requests

**Example Test**:
```python
import pytest
import pytest_asyncio
from httpx import AsyncClient

@pytest_asyncio.fixture
async def hn_client():
    async with AsyncClient(base_url="https://hn.algolia.com/api/v1") as client:
        yield client

@pytest.mark.asyncio
async def test_search_stories(hn_client):
    response = await hn_client.get("/search", params={"query": "python", "tags": "story"})
    assert response.status_code == 200
    data = response.json()
    assert "hits" in data
    assert data["nbHits"] > 0
```

### Code Quality: Ruff
**Why Ruff**:
- Single tool replacing Black, isort, Flake8, pylint
- 10-100x faster than alternatives
- Auto-fixes most issues
- Comprehensive rule set

**Configuration** (pyproject.toml):
```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "ARG", # flake8-unused-arguments
    "SIM", # flake8-simplify
]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Type Checking: mypy
**Configuration**:
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## Rate Limiting Strategy

### Implementation Approach
```python
from datetime import datetime, timedelta
from collections import deque

class RateLimiter:
    """Simple sliding window rate limiter"""
    
    def __init__(self, max_requests: int = 10000, window_hours: int = 1):
        self.max_requests = max_requests
        self.window = timedelta(hours=window_hours)
        self.requests: deque[datetime] = deque()
    
    async def acquire(self) -> bool:
        """Check if request can proceed"""
        now = datetime.now()
        cutoff = now - self.window
        
        # Remove old requests
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()
        
        if len(self.requests) >= self.max_requests:
            return False
        
        self.requests.append(now)
        return True
```

## Error Handling Patterns

### Retry with Exponential Backoff
```python
import asyncio
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from httpx import HTTPStatusError, NetworkError

@retry(
    retry=retry_if_exception_type((HTTPStatusError, NetworkError)),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3)
)
async def fetch_with_retry(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
```

### Custom Exceptions
```python
class HNAPIError(Exception):
    """Base exception for HN API errors"""
    pass

class RateLimitExceeded(HNAPIError):
    """Raised when rate limit is exceeded"""
    pass

class ItemNotFound(HNAPIError):
    """Raised when item/user not found"""
    pass
```

## MCP Tool Design

### Tool Catalog
```python
TOOLS = [
    # Search Tools
    "search_hn",              # General search by relevance
    "search_hn_by_date",      # Search sorted by date
    "get_front_page",         # Current front page
    "get_latest_stories",     # Latest stories
    "get_latest_comments",    # Latest comments
    
    # Item Tools
    "get_item",               # Get item by ID
    "get_story_comments",     # Get story with all comments
    
    # User Tools
    "get_user",               # Get user profile
    "get_user_stories",       # Get user's stories
    "get_user_comments",      # Get user's comments
    
    # Advanced Filters
    "search_by_time_range",   # Time-bounded search
    "search_by_metrics",      # Filter by points/comments
]
```

### Schema Example
```python
@app.tool()
async def search_hn(
    query: str,
    tags: list[str] | None = None,
    page: int = 0,
    hits_per_page: int = 20,
    numeric_filters: list[str] | None = None
) -> dict:
    """
    Search HackerNews content sorted by relevance.
    
    Args:
        query: Full-text search query
        tags: Filter tags (story, comment, author_USERNAME, etc.)
        page: Page number (0-indexed)
        hits_per_page: Results per page (max 1000)
        numeric_filters: Numeric filters (e.g., ["points>100"])
        
    Returns:
        Search results with hits and pagination metadata
        
    Examples:
        >>> await search_hn("python", tags=["story"], hits_per_page=10)
        >>> await search_hn("machine learning", numeric_filters=["points>50"])
    """
    # Implementation
```

## Dependency Decision Matrix

| Package | Version | Justification | Alternatives Rejected |
|---------|---------|---------------|----------------------|
| mcp | 1.1.0+ | Official SDK, protocol compliance | Custom JSON-RPC (reinventing) |
| httpx | 0.27.0+ | Async support, HTTP/2, battle-tested | requests (no async), aiohttp (complex) |
| pydantic | 2.10.0+ | Type-safe validation, JSON serialization | dataclasses (no validation), attrs (less popular) |
| pytest | 8.3.0+ | Industry standard, excellent ecosystem | unittest (verbose), nose (deprecated) |
| ruff | 0.8.0+ | Fast, comprehensive, single tool | Black+isort+Flake8 (multiple tools) |
| mypy | 1.13.0+ | Best-in-class type checker | pyright (less mature), pytype (slower) |

## Architecture Decision Records (ADRs)

### ADR-001: Use httpx for HTTP Client
**Decision**: Use httpx over requests or aiohttp

**Rationale**:
- Native async/await (required for MCP)
- Better API than aiohttp
- Excellent documentation and adoption
- Proven performance and reliability

**Consequences**:
- All HTTP calls must be async
- Requires AsyncClient context manager pattern

### ADR-002: Stateless Design
**Decision**: Keep server completely stateless (no caching)

**Rationale**:
- Simplifies architecture
- Avoids cache invalidation complexity
- Fresh data always returned
- Follows constitution: start simple

**Consequences**:
- Every request hits HN API
- Must respect rate limits carefully
- Future enhancement: add caching layer

### ADR-003: Pydantic v2 for Validation
**Decision**: Use Pydantic v2 for all data models

**Rationale**:
- Automatic validation from type hints
- Excellent error messages
- JSON serialization included
- Integration with MCP patterns

**Consequences**:
- Must handle Pydantic validation errors
- Models mirror API response structure

## Testing Strategy Details

### Contract Tests
Verify MCP protocol compliance:
```python
async def test_tool_schema():
    """Verify tool schemas are valid MCP format"""
    tools = await app.list_tools()
    
    for tool in tools:
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        assert tool["inputSchema"]["type"] == "object"
```

### Integration Tests
Test against real HN API:
```python
@pytest.mark.integration
async def test_search_integration():
    """Test real search against HN API"""
    result = await search_hn("python", tags=["story"], hits_per_page=5)
    
    assert result["nbHits"] > 0
    assert len(result["hits"]) <= 5
    assert all(hit["author"] for hit in result["hits"])
```

### Unit Tests
Test individual components:
```python
def test_rate_limiter():
    """Test rate limiting logic"""
    limiter = RateLimiter(max_requests=5, window_hours=1)
    
    # Should allow first 5
    for _ in range(5):
        assert limiter.acquire()
    
    # Should block 6th
    assert not limiter.acquire()
```

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| HN API rate limit hit | High | Medium | Client-side rate limiting, request queuing |
| API downtime | Medium | Low | Retry logic, clear error messages |
| Breaking API changes | High | Low | Version pinning, monitoring, tests |
| MCP protocol changes | Medium | Low | Use official SDK, follow updates |
| Performance issues | Medium | Low | Async patterns, connection pooling |

## Open Questions

1. ✅ **Caching strategy?** - No caching in v1 (keep stateless per ADR-002)
2. ✅ **Rate limit handling?** - Client-side tracking, reject requests proactively
3. ✅ **Error format?** - Follow MCP error conventions, structured errors
4. ✅ **Pagination strategy?** - Pass through HN API pagination params
5. ✅ **Testing approach?** - Contract + Integration + Unit per constitution

## Next Steps

1. **Phase 1**: Create detailed data models (data-model.md)
2. **Phase 1**: Design tool contracts (contracts/*.json)
3. **Phase 1**: Write quickstart guide (quickstart.md)
4. **Phase 2**: Break down implementation tasks (tasks.md)
5. **Phase 3**: TDD implementation following task list

## References

- HN API Documentation: https://hn.algolia.com/api
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Pydantic v2: https://docs.pydantic.dev/latest/
- httpx: https://www.python-httpx.org/
- Ruff: https://docs.astral.sh/ruff/
