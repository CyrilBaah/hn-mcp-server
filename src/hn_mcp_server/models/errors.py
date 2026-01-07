"""Error models for HackerNews MCP Server."""

from typing import Any, Literal

from pydantic import BaseModel

ErrorCode = Literal[
    "INVALID_PARAMETER",
    "RATE_LIMIT_EXCEEDED",
    "API_ERROR",
    "NETWORK_ERROR",
    "NOT_FOUND",
    "TIMEOUT",
]


class ErrorDetails(BaseModel):
    """Error details with additional context."""

    code: ErrorCode
    message: str
    details: dict[str, Any] | None = None

    model_config = {"frozen": True}


class APIErrorResponse(BaseModel):
    """API error response wrapper."""

    error: ErrorDetails

    model_config = {"frozen": True}
