"""User-related data models for HackerNews API."""

from pydantic import BaseModel


class User(BaseModel):
    """User profile from HN API."""

    username: str
    about: str | None = None
    karma: int
    created: str | None = None  # ISO date string
    created_at: str | None = None  # Alternative field name
    created_at_i: int | None = None  # Unix timestamp

    model_config = {"frozen": True, "populate_by_name": True}
