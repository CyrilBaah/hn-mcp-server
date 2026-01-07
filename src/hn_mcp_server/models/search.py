"""Search-related data models for HackerNews API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Hit(BaseModel):
    """Individual search result item (story, comment, poll, etc.)."""

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
    highlight_result: dict[str, Any] = Field(default_factory=dict, alias="_highlightResult")

    model_config = {"populate_by_name": True}


class SearchResult(BaseModel):
    """Response from HN search API (both /search and /search_by_date)."""

    hits: list[Hit]
    page: int
    nb_hits: int = Field(alias="nbHits")
    nb_pages: int = Field(alias="nbPages")
    hits_per_page: int = Field(alias="hitsPerPage")
    processing_time_ms: int = Field(alias="processingTimeMS")
    query: str
    params: str

    model_config = {"populate_by_name": True, "frozen": True}


class SearchParams(BaseModel):
    """Parameters for search endpoints."""

    query: str = ""
    tags: list[str] = Field(default_factory=list)
    page: int = Field(default=0, ge=0)
    hits_per_page: int = Field(default=20, ge=1, le=1000)
    numeric_filters: list[str] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate tag format."""
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
        """Validate numeric filter format."""
        valid_fields = {"created_at_i", "points", "num_comments"}

        for filter_str in v:
            # Extract field (before any operator)
            field = filter_str.split("<")[0].split(">")[0].split("=")[0]

            if field not in valid_fields:
                raise ValueError(f"Invalid numeric field: {field}")

        return v

    def to_query_params(self) -> dict[str, str | int]:
        """Convert to API query parameters."""
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
