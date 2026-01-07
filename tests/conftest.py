"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def mock_hn_api_url() -> str:
    """Return mock HN API base URL."""
    return "https://hn.algolia.com/api/v1"


@pytest.fixture
def sample_search_response() -> dict:
    """Return sample search API response."""
    return {
        "hits": [
            {
                "objectID": "1",
                "created_at": "2025-01-05T12:00:00.000Z",
                "created_at_i": 1736078400,
                "author": "testuser",
                "title": "Test Story",
                "url": "https://example.com",
                "points": 100,
                "num_comments": 50,
                "_tags": ["story", "front_page"],
            }
        ],
        "page": 0,
        "nbHits": 1,
        "nbPages": 1,
        "hitsPerPage": 20,
        "processingTimeMS": 1,
        "query": "test",
        "params": "query=test",
    }


@pytest.fixture
def sample_item_response() -> dict:
    """Return sample item API response."""
    return {
        "id": 1,
        "created_at": "2025-01-05T12:00:00.000Z",
        "created_at_i": 1736078400,
        "author": "testuser",
        "type": "story",
        "title": "Test Story",
        "url": "https://example.com",
        "text": None,
        "points": 100,
        "parent_id": None,
        "children": [],
    }


@pytest.fixture
def sample_user_response() -> dict:
    """Return sample user API response."""
    return {
        "username": "testuser",
        "about": "Test user bio",
        "karma": 5000,
        "created_at": "2020-01-01T00:00:00.000Z",
        "created_at_i": 1577836800,
    }
