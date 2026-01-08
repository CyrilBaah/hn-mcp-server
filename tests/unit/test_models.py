"""Unit tests for Pydantic models."""


import pytest
from pydantic import ValidationError

from hn_mcp_server.models import (
    APIErrorResponse,
    ErrorDetails,
    Hit,
    Item,
    SearchParams,
    SearchResult,
    User,
)


class TestSearchResult:
    """Test SearchResult model."""

    def test_valid_search_result(self, sample_search_response):
        """Test parsing valid search result."""
        result = SearchResult.model_validate(sample_search_response)

        assert result.page == 0
        assert result.nb_hits == 1
        assert result.nb_pages == 1
        assert result.hits_per_page == 20
        assert result.query == "test"
        assert len(result.hits) == 1

    def test_search_result_aliases(self):
        """Test field aliases work correctly."""
        data = {
            "hits": [],
            "page": 0,
            "nbHits": 100,
            "nbPages": 5,
            "hitsPerPage": 20,
            "processingTimeMS": 5,
            "query": "test",
            "params": "query=test",
        }

        result = SearchResult.model_validate(data)

        assert result.nb_hits == 100
        assert result.nb_pages == 5
        assert result.hits_per_page == 20
        assert result.processing_time_ms == 5

    def test_search_result_frozen(self, sample_search_response):
        """Test SearchResult is immutable."""
        result = SearchResult.model_validate(sample_search_response)

        with pytest.raises(ValidationError):
            result.page = 1


class TestHit:
    """Test Hit model."""

    def test_story_hit(self):
        """Test parsing story hit."""
        data = {
            "objectID": "123",
            "created_at": "2025-01-05T12:00:00.000Z",
            "created_at_i": 1736078400,
            "author": "testuser",
            "title": "Test Story",
            "url": "https://example.com",
            "points": 100,
            "num_comments": 50,
            "_tags": ["story"],
        }

        hit = Hit.model_validate(data)

        assert hit.object_id == "123"
        assert hit.author == "testuser"
        assert hit.title == "Test Story"
        assert hit.points == 100
        assert hit.num_comments == 50
        assert "story" in hit.tags

    def test_comment_hit(self):
        """Test parsing comment hit."""
        data = {
            "objectID": "456",
            "created_at": "2025-01-05T12:00:00.000Z",
            "created_at_i": 1736078400,
            "author": "commenter",
            "comment_text": "Great article!",
            "parent_id": 123,
            "story_id": 100,
            "_tags": ["comment"],
        }

        hit = Hit.model_validate(data)

        assert hit.object_id == "456"
        assert hit.comment_text == "Great article!"
        assert hit.parent_id == 123
        assert hit.story_id == 100
        assert hit.title is None


class TestSearchParams:
    """Test SearchParams model."""

    def test_valid_params(self):
        """Test valid search parameters."""
        params = SearchParams(
            query="python",
            tags=["story"],
            hits_per_page=50,
        )

        assert params.query == "python"
        assert params.tags == ["story"]
        assert params.hits_per_page == 50

    def test_invalid_hits_per_page(self):
        """Test invalid hits_per_page validation."""
        with pytest.raises(ValidationError):
            SearchParams(hits_per_page=2000)

        with pytest.raises(ValidationError):
            SearchParams(hits_per_page=0)

    def test_invalid_tag(self):
        """Test invalid tag validation."""
        with pytest.raises(ValidationError):
            SearchParams(tags=["invalid_tag"])

    def test_valid_author_tag(self):
        """Test author_ tag is valid."""
        params = SearchParams(tags=["author_pg"])
        assert "author_pg" in params.tags

    def test_valid_story_tag(self):
        """Test story_ tag is valid."""
        params = SearchParams(tags=["story_12345"])
        assert "story_12345" in params.tags

    def test_to_query_params(self):
        """Test conversion to API query params."""
        params = SearchParams(
            query="python",
            tags=["story", "show_hn"],
            hits_per_page=50,
            numeric_filters=["points>100"],
        )

        query_params = params.to_query_params()

        assert query_params["query"] == "python"
        assert query_params["tags"] == "story,show_hn"
        assert query_params["hitsPerPage"] == 50
        assert query_params["numericFilters"] == "points>100"

    def test_invalid_numeric_filter(self):
        """Test invalid numeric filter validation."""
        with pytest.raises(ValidationError):
            SearchParams(numeric_filters=["invalid_field>100"])


class TestItem:
    """Test Item model."""

    def test_story_item(self, sample_item_response):
        """Test parsing story item."""
        item = Item.model_validate(sample_item_response)

        assert item.id == 1
        assert item.author == "testuser"
        assert item.title == "Test Story"
        assert item.is_story is True
        assert item.is_comment is False

    def test_comment_item(self):
        """Test parsing comment item."""
        data = {
            "id": 2,
            "created_at": "2025-01-05T12:00:00.000Z",
            "created_at_i": 1736078400,
            "author": "commenter",
            "type": "comment",
            "text": "Great!",
            "parent_id": 1,
            "children": [],
        }

        item = Item.model_validate(data)

        assert item.is_story is False
        assert item.is_comment is True

    def test_nested_children(self):
        """Test nested children parsing."""
        data = {
            "id": 1,
            "created_at": "2025-01-05T12:00:00.000Z",
            "created_at_i": 1736078400,
            "author": "author",
            "type": "story",
            "title": "Story",
            "children": [
                {
                    "id": 2,
                    "created_at": "2025-01-05T12:00:00.000Z",
                    "created_at_i": 1736078400,
                    "author": "commenter",
                    "type": "comment",
                    "text": "Comment 1",
                    "parent_id": 1,
                    "children": [],
                }
            ],
        }

        item = Item.model_validate(data)

        assert len(item.children) == 1
        assert item.children[0].id == 2
        assert item.total_comments() == 1


class TestUser:
    """Test User model."""

    def test_valid_user(self, sample_user_response):
        """Test parsing valid user."""
        user = User.model_validate(sample_user_response)

        assert user.username == "testuser"
        assert user.about == "Test user bio"
        assert user.karma == 5000

    def test_user_frozen(self, sample_user_response):
        """Test User is immutable."""
        user = User.model_validate(sample_user_response)

        with pytest.raises(ValidationError):
            user.karma = 6000


class TestErrorModels:
    """Test error models."""

    def test_error_details(self):
        """Test ErrorDetails model."""
        error = ErrorDetails(
            code="API_ERROR",
            message="Something went wrong",
            details={"status": 500},
        )

        assert error.code == "API_ERROR"
        assert error.message == "Something went wrong"
        assert error.details["status"] == 500

    def test_api_error_response(self):
        """Test APIErrorResponse model."""
        response = APIErrorResponse(
            error=ErrorDetails(
                code="NOT_FOUND",
                message="Resource not found",
            )
        )

        assert response.error.code == "NOT_FOUND"
        assert response.error.message == "Resource not found"
