"""Item-related data models for HackerNews API."""

from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, HttpUrl


class Item(BaseModel):
    """Full item from /items endpoint with nested children."""

    id: int
    created_at: datetime
    created_at_i: int
    author: str
    type: str

    # Optional fields depending on item type
    title: str | None = None
    url: HttpUrl | None = None
    text: str | None = None
    points: int | None = None
    parent_id: int | None = None

    # Nested children (recursive)
    children: list[Self] = Field(default_factory=list)

    model_config = {"populate_by_name": True}

    @property
    def is_story(self) -> bool:
        """Check if item is a story."""
        return self.title is not None and self.parent_id is None

    @property
    def is_comment(self) -> bool:
        """Check if item is a comment."""
        return self.parent_id is not None

    def flatten_comments(self) -> list[Self]:
        """Flatten nested comment tree to list."""
        comments = []
        for child in self.children:
            comments.append(child)
            comments.extend(child.flatten_comments())
        return comments

    def total_comments(self) -> int:
        """Count total comments including nested."""
        return len(self.flatten_comments())
