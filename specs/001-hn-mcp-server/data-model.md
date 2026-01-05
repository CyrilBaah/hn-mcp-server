# Data Models: HackerNews MCP Server

**Phase**: 1 - Data Model Design  
**Date**: 2025-01-05  
**Status**: Complete

## Overview

This document defines all Pydantic models for the HackerNews MCP Server. Models handle validation, serialization, and provide type safety for all API interactions.

## Core Principles

1. **Type Safety**: All fields have explicit types with Optional where nullable
2. **Validation**: Pydantic validates all input/output automatically
3. **Serialization**: Models handle JSON conversion for API responses
4. **Aliases**: Use field aliases to map HN API naming to Pythonic names
5. **Immutability**: Models are frozen where appropriate for safety

## HackerNews API Response Models

### SearchResult

Primary response model for search endpoints.

```python
from pydantic import BaseModel, Field
from typing import Any

class SearchResult(BaseModel):
    """Response from HN search API (both /search and /search_by_date)"""
    
    hits: list[dict[str, Any]]
    page: int
    nb_hits: int = Field(alias="nbHits")
    nb_pages: int = Field(alias="nbPages")
    hits_per_page: int = Field(alias="hitsPerPage")
    processing_time_ms: int = Field(alias="processingTimeMS")
    query: str
    params: str
    
    model_config = {
        "populate_by_name": True,  # Allow both alias and field name
        "frozen": True  # Immutable after creation
    }
```

**Usage**:
```python
# Parse API response
data = response.json()
result = SearchResult.model_validate(data)

# Access fields
print(f"Found {result.nb_hits} results")
print(f"Page {result.page + 1} of {result.nb_pages}")
```

### Hit (Search Result Item)

Individual item in search results.

```python
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Any

class Hit(BaseModel):
    """Individual search result item (story, comment, poll, etc.)"""
    
    object_id: str = Field(alias="objectID")
    created_at: datetime
    created_at_i: int  # Unix timestamp
    author: str
    
    # Story fields (null for comments)
    title: str | None = None
    url: HttpUrl | None = None
    points: int | None = None
    num_comments: int = 0
    story_text: str | None = None
    
    # Comment fields (null for stories)
    comment_text: str | None = None
    parent_id: int | None = None
    story_id: int | None = None
    
    # Metadata
    tags: list[str] = Field(default_factory=list, alias="_tags")
    highlight_result: dict[str, Any] = Field(
        default_factory=dict,
        alias="_highlightResult"
    )
    
    model_config = {
        "populate_by_name": True
    }
```

**Usage**:
```python
# Parse individual hit
hit = Hit.model_validate(hit_data)

# Type-safe access
if hit.title:
    print(f"Story: {hit.title}")
if hit.comment_text:
    print(f"Comment: {hit.comment_text}")
```

### Item (Full Item with Children)

Complete item from /items/{id} endpoint with nested comments.

```python
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Self

class Item(BaseModel):
    """Full item from /items endpoint with nested children"""
    
    id: int
    created_at: datetime
    author: str
    
    # Optional fields depending on item type
    title: str | None = None
    url: HttpUrl | None = None
    text: str | None = None
    points: int | None = None
    parent_id: int | None = None
    
    # Nested children (recursive)
    children: list[Self] = Field(default_factory=list)
    
    model_config = {
        "populate_by_name": True
    }
    
    @property
    def is_story(self) -> bool:
        """Check if item is a story"""
        return self.title is not None and self.parent_id is None
    
    @property
    def is_comment(self) -> bool:
        """Check if item is a comment"""
        return self.parent_id is not None
    
    def flatten_comments(self) -> list[Self]:
        """Flatten nested comment tree to list"""
        comments = []
        for child in self.children:
            comments.append(child)
            comments.extend(child.flatten_comments())
        return comments
    
    def total_comments(self) -> int:
        """Count total comments including nested"""
        return len(self.flatten_comments())
```

**Usage**:
```python
# Parse item with nested children
item = Item.model_validate(item_data)

# Access nested data
print(f"Story: {item.title}")
print(f"Direct replies: {len(item.children)}")
print(f"Total comments: {item.total_comments()}")

# Iterate through all comments
for comment in item.flatten_comments():
    print(f"{comment.author}: {comment.text}")
```

### User

User profile from /users/{username} endpoint.

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    """User profile from HN API"""
    
    username: str
    about: str | None = None
    karma: int
    created: str | None = None  # ISO date string
    
    model_config = {
        "frozen": True
    }
```

**Usage**:
```python
# Parse user profile
user = User.model_validate(user_data)

# Display profile
print(f"{user.username} - {user.karma:,} karma")
if user.about:
    print(f"About: {user.about}")
```

## Request Parameter Models

### SearchParams

Input validation for search requests.

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class SearchParams(BaseModel):
    """Parameters for search endpoints"""
    
    query: str = ""
    tags: list[str] = Field(default_factory=list)
    page: int = Field(default=0, ge=0)
    hits_per_page: int = Field(default=20, ge=1, le=1000)
    numeric_filters: list[str] = Field(default_factory=list)
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate tag format"""
        valid_types = {"story", "comment", "poll", "pollopt", "show_hn", "ask_hn", "front_page"}
        
        for tag in v:
            # Check if it's a basic tag
            if tag in valid_types:
                continue
            # Check if it's author_ tag
            if tag.startswith("author_"):
                continue
            # Check if it's story_ tag
            if tag.startswith("story_"):
                continue
            # Check if it's OR group
            if tag.startswith("(") and tag.endswith(")"):
                continue
            
            raise ValueError(f"Invalid tag: {tag}")
        
        return v
    
    @field_validator("numeric_filters")
    @classmethod
    def validate_numeric_filters(cls, v: list[str]) -> list[str]:
        """Validate numeric filter format"""
        valid_fields = {"created_at_i", "points", "num_comments"}
        valid_ops = {"<", "<=", "=", ">", ">="}
        
        for filter_str in v:
            # Extract field and operator
            field = filter_str.split("<")[0].split(">")[0].split("=")[0]
            
            if field not in valid_fields:
                raise ValueError(f"Invalid numeric field: {field}")
        
        return v
    
    def to_query_params(self) -> dict[str, str | int]:
        """Convert to API query parameters"""
        params: dict[str, str | int] = {}
        
        if self.query:
            params["query"] = self.query
        if self.tags:
            params["tags"] = ",".join(self.tags)
        if self.page:
            params["page"] = self.page
        if self.hits_per_page != 20:
            params["hitsPerPage"] = self.hits_per_page
        if self.numeric_filters:
            params["numericFilters"] = ",".join(self.numeric_filters)
        
        return params
```

**Usage**:
```python
# Validate search parameters
params = SearchParams(
    query="python",
    tags=["story", "show_hn"],
    hits_per_page=50,
    numeric_filters=["points>100"]
)

# Convert to API params
api_params = params.to_query_params()
# {"query": "python", "tags": "story,show_hn", "hitsPerPage": 50, "numericFilters": "points>100"}
```

### TimeRangeParams

Parameters for time-bounded searches.

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class TimeRangeParams(BaseModel):
    """Parameters for time-range searches"""
    
    start_timestamp: int = Field(ge=0)
    end_timestamp: int = Field(ge=0)
    query: str = ""
    tags: list[str] = Field(default_factory=list)
    page: int = Field(default=0, ge=0)
    hits_per_page: int = Field(default=20, ge=1, le=1000)
    
    @field_validator("end_timestamp")
    @classmethod
    def validate_time_range(cls, v: int, info) -> int:
        """Ensure end is after start"""
        if "start_timestamp" in info.data and v < info.data["start_timestamp"]:
            raise ValueError("end_timestamp must be after start_timestamp")
        return v
    
    def to_search_params(self) -> SearchParams:
        """Convert to SearchParams with numeric filters"""
        numeric_filters = [
            f"created_at_i>{self.start_timestamp}",
            f"created_at_i<{self.end_timestamp}"
        ]
        
        return SearchParams(
            query=self.query,
            tags=self.tags,
            page=self.page,
            hits_per_page=self.hits_per_page,
            numeric_filters=numeric_filters
        )
```

### MetricsParams

Parameters for filtering by points/comments.

```python
from pydantic import BaseModel, Field

class MetricsParams(BaseModel):
    """Parameters for metrics-based filtering"""
    
    min_points: int | None = Field(default=None, ge=0)
    min_comments: int | None = Field(default=None, ge=0)
    query: str = ""
    tags: list[str] = Field(default_factory=list)
    page: int = Field(default=0, ge=0)
    hits_per_page: int = Field(default=20, ge=1, le=1000)
    
    def to_search_params(self) -> SearchParams:
        """Convert to SearchParams with numeric filters"""
        numeric_filters = []
        
        if self.min_points is not None:
            numeric_filters.append(f"points>={self.min_points}")
        if self.min_comments is not None:
            numeric_filters.append(f"num_comments>={self.min_comments}")
        
        return SearchParams(
            query=self.query,
            tags=self.tags,
            page=self.page,
            hits_per_page=self.hits_per_page,
            numeric_filters=numeric_filters
        )
```

## Error Models

### APIError

Structured error responses.

```python
from pydantic import BaseModel
from typing import Any, Literal

ErrorCode = Literal[
    "INVALID_PARAMETER",
    "RATE_LIMIT_EXCEEDED",
    "API_ERROR",
    "NETWORK_ERROR",
    "NOT_FOUND",
    "TIMEOUT"
]

class ErrorDetails(BaseModel):
    """Error details with additional context"""
    
    code: ErrorCode
    message: str
    details: dict[str, Any] | None = None
    
    model_config = {
        "frozen": True
    }

class APIErrorResponse(BaseModel):
    """API error response wrapper"""
    
    error: ErrorDetails
    
    model_config = {
        "frozen": True
    }
```

**Usage**:
```python
# Create error response
error = APIErrorResponse(
    error=ErrorDetails(
        code="RATE_LIMIT_EXCEEDED",
        message="API rate limit reached",
        details={"retry_after": 3600}
    )
)

# Serialize to JSON
error_json = error.model_dump_json()
```

## Model Usage in MCP Tools

### Example Tool Implementation

```python
from mcp.server import Server
from hn_mcp_server.models import SearchParams, SearchResult, Hit

app = Server("hn-mcp-server")

@app.tool()
async def search_hn(
    query: str,
    tags: list[str] | None = None,
    page: int = 0,
    hits_per_page: int = 20,
    numeric_filters: list[str] | None = None
) -> dict:
    """Search HackerNews content"""
    
    # Validate parameters
    params = SearchParams(
        query=query,
        tags=tags or [],
        page=page,
        hits_per_page=hits_per_page,
        numeric_filters=numeric_filters or []
    )
    
    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://hn.algolia.com/api/v1/search",
            params=params.to_query_params()
        )
        response.raise_for_status()
    
    # Parse and validate response
    result = SearchResult.model_validate(response.json())
    
    # Convert to dict for MCP response
    return result.model_dump(by_alias=True)
```

## Model Testing

### Validation Tests

```python
import pytest
from hn_mcp_server.models import SearchParams, TimeRangeParams

def test_search_params_validation():
    """Test SearchParams validation"""
    # Valid params
    params = SearchParams(
        query="python",
        tags=["story"],
        hits_per_page=50
    )
    assert params.query == "python"
    
    # Invalid hits_per_page
    with pytest.raises(ValueError):
        SearchParams(hits_per_page=2000)
    
    # Invalid tag
    with pytest.raises(ValueError):
        SearchParams(tags=["invalid_tag"])

def test_time_range_validation():
    """Test TimeRangeParams validation"""
    # Valid range
    params = TimeRangeParams(
        start_timestamp=1000,
        end_timestamp=2000
    )
    
    # Invalid range (end before start)
    with pytest.raises(ValueError):
        TimeRangeParams(
            start_timestamp=2000,
            end_timestamp=1000
        )
```

### Serialization Tests

```python
def test_search_result_parsing():
    """Test SearchResult deserialization"""
    api_response = {
        "hits": [],
        "page": 0,
        "nbHits": 100,
        "nbPages": 5,
        "hitsPerPage": 20,
        "processingTimeMS": 5,
        "query": "test",
        "params": "query=test"
    }
    
    result = SearchResult.model_validate(api_response)
    
    assert result.nb_hits == 100
    assert result.nb_pages == 5
    assert result.hits_per_page == 20
```

## Model Directory Structure

```
src/hn_mcp_server/models/
├── __init__.py          # Export all models
├── search.py            # SearchResult, Hit, SearchParams
├── item.py              # Item (with recursive children)
├── user.py              # User profile models
├── params.py            # TimeRangeParams, MetricsParams
└── errors.py            # Error models
```

## Best Practices

1. **Always Validate**: Use Pydantic models for all API data
2. **Use Aliases**: Keep Pythonic names with API aliases
3. **Frozen Models**: Make response models immutable
4. **Type Hints**: Explicit types for all fields
5. **Validators**: Custom validation for complex rules
6. **Helper Methods**: Add utility methods to models
7. **Documentation**: Docstrings on all models and fields

## References

- Pydantic v2 Documentation: https://docs.pydantic.dev/latest/
- HN API Response Formats: https://hn.algolia.com/api
- MCP Type System: https://spec.modelcontextprotocol.io
