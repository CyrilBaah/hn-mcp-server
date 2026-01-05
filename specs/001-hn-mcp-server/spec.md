# Feature Specification: HackerNews MCP Server

**Version**: 1.0.0  
**Status**: Draft  
**Created**: 2025-01-05  
**Author**: Development Team

## Overview

A Model Context Protocol (MCP) server that provides programmatic access to HackerNews content through the official HN Algolia API. This enables AI assistants and other MCP clients to search, retrieve, and analyze HackerNews stories, comments, and user profiles.

## Objectives

### Primary Goals
1. Expose all HackerNews API capabilities as MCP tools
2. Provide type-safe, validated interfaces for HN data
3. Handle rate limiting and error scenarios gracefully
4. Deliver comprehensive search and filtering capabilities

### Success Criteria
- All HN API endpoints accessible via MCP tools
- Response time < 2s p95 for API calls
- 100% MCP protocol compliance
- 80%+ test coverage
- Zero data corruption or invalid responses

## Functional Requirements

### FR1: Search Tools

#### FR1.1: Search by Relevance
- **Tool**: `search_hn`
- **Description**: Search HackerNews content sorted by relevance, then points, then comments
- **Parameters**:
  - `query` (string, required): Full-text search query
  - `tags` (string[], optional): Filter by tags (story, comment, poll, pollopt, show_hn, ask_hn, front_page, author_USERNAME, story_ID)
  - `page` (integer, optional, default: 0): Page number for pagination
  - `hitsPerPage` (integer, optional, default: 20, max: 1000): Results per page
  - `numericFilters` (string[], optional): Numeric filters (created_at_i, points, num_comments)
- **Returns**: Search results with hits, pagination metadata, processing time

#### FR1.2: Search by Date
- **Tool**: `search_hn_by_date`
- **Description**: Search HackerNews content sorted by date (most recent first)
- **Parameters**: Same as FR1.1
- **Returns**: Same as FR1.1

#### FR1.3: Front Page Stories
- **Tool**: `get_front_page`
- **Description**: Retrieve current front page stories
- **Parameters**:
  - `page` (integer, optional): Page number
  - `hitsPerPage` (integer, optional): Results per page
- **Returns**: Front page stories with metadata

#### FR1.4: Latest Stories
- **Tool**: `get_latest_stories`
- **Description**: Retrieve most recent stories
- **Parameters**:
  - `page` (integer, optional): Page number
  - `hitsPerPage` (integer, optional): Results per page
- **Returns**: Latest stories sorted by creation date

#### FR1.5: Latest Comments
- **Tool**: `get_latest_comments`
- **Description**: Retrieve most recent comments
- **Parameters**:
  - `page` (integer, optional): Page number
  - `hitsPerPage` (integer, optional): Results per page
- **Returns**: Latest comments sorted by creation date

### FR2: Item Retrieval Tools

#### FR2.1: Get Item by ID
- **Tool**: `get_item`
- **Description**: Retrieve a specific item (story, comment, poll, etc.) by ID
- **Parameters**:
  - `id` (integer, required): Item ID
- **Returns**: Complete item with nested children (comments)

#### FR2.2: Get Story with Comments
- **Tool**: `get_story_comments`
- **Description**: Retrieve a story and all its comments
- **Parameters**:
  - `story_id` (integer, required): Story ID
- **Returns**: Story with full comment tree

### FR3: User Tools

#### FR3.1: Get User Profile
- **Tool**: `get_user`
- **Description**: Retrieve user profile information
- **Parameters**:
  - `username` (string, required): HackerNews username
- **Returns**: User profile with username, about, karma

#### FR3.2: Get User Stories
- **Tool**: `get_user_stories`
- **Description**: Retrieve all stories submitted by a user
- **Parameters**:
  - `username` (string, required): HackerNews username
  - `page` (integer, optional): Page number
  - `hitsPerPage` (integer, optional): Results per page
- **Returns**: User's stories

#### FR3.3: Get User Comments
- **Tool**: `get_user_comments`
- **Description**: Retrieve all comments by a user
- **Parameters**:
  - `username` (string, required): HackerNews username
  - `page` (integer, optional): Page number
  - `hitsPerPage` (integer, optional): Results per page
- **Returns**: User's comments

### FR4: Advanced Filtering

#### FR4.1: Filter by Time Range
- **Tool**: `search_by_time_range`
- **Description**: Search items within a specific time range
- **Parameters**:
  - `start_timestamp` (integer, required): Start time (Unix timestamp)
  - `end_timestamp` (integer, required): End time (Unix timestamp)
  - `tags` (string[], optional): Item types to include
  - `query` (string, optional): Search query
- **Returns**: Filtered results

#### FR4.2: Filter by Points/Comments
- **Tool**: `search_by_metrics`
- **Description**: Search items with minimum points or comments
- **Parameters**:
  - `min_points` (integer, optional): Minimum points
  - `min_comments` (integer, optional): Minimum number of comments
  - `query` (string, optional): Search query
  - `tags` (string[], optional): Item types
- **Returns**: Filtered results

## Non-Functional Requirements

### NFR1: Performance
- API response time < 2s at p95
- Handle concurrent requests efficiently
- Memory usage < 50MB under normal load

### NFR2: Reliability
- Graceful handling of HN API failures
- Automatic retry with exponential backoff
- Rate limit compliance (10,000 req/hour)
- Circuit breaker for repeated failures

### NFR3: Security
- Input validation on all parameters
- Sanitize output to prevent injection
- No sensitive data logging
- HTTPS for all API calls

### NFR4: Observability
- Structured logging (JSON format)
- Log all API requests/responses
- Error tracking with stack traces
- Performance metrics (latency, throughput)

### NFR5: Maintainability
- Type hints on all functions
- Comprehensive docstrings
- Clear error messages
- Modular, testable code

## Data Models

### SearchResult
```python
{
  "hits": [Hit],
  "page": int,
  "nbHits": int,
  "nbPages": int,
  "hitsPerPage": int,
  "processingTimeMS": int,
  "query": str,
  "params": str
}
```

### Hit (Story/Comment)
```python
{
  "objectID": str,
  "title": str | null,
  "url": str | null,
  "author": str,
  "points": int | null,
  "story_text": str | null,
  "comment_text": str | null,
  "num_comments": int,
  "created_at": str,
  "created_at_i": int,
  "_tags": [str],
  "_highlightResult": dict
}
```

### Item (Full)
```python
{
  "id": int,
  "created_at": str,
  "author": str,
  "title": str | null,
  "url": str | null,
  "text": str | null,
  "points": int | null,
  "parent_id": int | null,
  "children": [Item]
}
```

### User
```python
{
  "username": str,
  "about": str | null,
  "karma": int
}
```

## Error Handling

### Error Codes
- `INVALID_PARAMETER`: Invalid input parameter
- `RATE_LIMIT_EXCEEDED`: HN API rate limit reached
- `API_ERROR`: HN API returned error
- `NETWORK_ERROR`: Network connectivity issue
- `NOT_FOUND`: Item/user not found
- `TIMEOUT`: Request timed out

### Error Response Format
```python
{
  "error": {
    "code": str,
    "message": str,
    "details": dict | null
  }
}
```

## Dependencies

### Required Packages
- `mcp` >= 1.0.0 - MCP SDK
- `httpx` >= 0.27.0 - Async HTTP client
- `pydantic` >= 2.0.0 - Data validation
- `python-dotenv` >= 1.0.0 - Configuration

### Development Packages
- `pytest` >= 8.0.0 - Testing framework
- `pytest-asyncio` >= 0.23.0 - Async test support
- `pytest-cov` >= 4.1.0 - Coverage reporting
- `mypy` >= 1.8.0 - Type checking
- `ruff` >= 0.1.0 - Linting and formatting
- `pre-commit` >= 3.6.0 - Git hooks

## Configuration

### Environment Variables
- `HN_API_BASE_URL` (default: "https://hn.algolia.com/api/v1")
- `HN_REQUEST_TIMEOUT` (default: 10 seconds)
- `HN_MAX_RETRIES` (default: 3)
- `LOG_LEVEL` (default: "INFO")

## Testing Strategy

### Unit Tests
- Model validation and serialization
- Tool parameter validation
- Rate limiting logic
- Error handling

### Integration Tests
- HN API client functionality
- End-to-end tool execution
- Error scenarios with API

### Contract Tests
- MCP protocol compliance
- Tool schema validation
- Response format verification

## Documentation Requirements

### Context7 Documentation
1. **API Reference**: Auto-generated from type hints and docstrings
2. **User Guide**: Installation, configuration, usage examples
3. **Integration Guide**: MCP client setup, tool catalog
4. **ADR**: Architecture decisions (why httpx, pydantic choices, etc.)
5. **Troubleshooting**: Common issues and solutions

### Code Examples
- Basic search
- Advanced filtering
- User profile lookup
- Front page monitoring
- Time-range queries

## Acceptance Criteria

1. ✅ All 13+ MCP tools implemented and tested
2. ✅ 80%+ code coverage with passing tests
3. ✅ MCP protocol compliance verified
4. ✅ Rate limiting prevents API abuse
5. ✅ Comprehensive error handling
6. ✅ Type hints on all public interfaces
7. ✅ Ruff linting passes with zero errors
8. ✅ mypy strict mode passes
9. ✅ Documentation complete in Context7
10. ✅ Installation guide works end-to-end

## Out of Scope

- Write operations (HN API is read-only)
- Authentication (HN API is public)
- Caching layer (keep stateless)
- Real-time updates (polling only)
- GraphQL interface (REST only)

## Future Enhancements

- Response caching for frequently accessed items
- WebSocket support for real-time updates
- Analytics/trending analysis tools
- Sentiment analysis integration
- Export to various formats (CSV, JSON, Markdown)
