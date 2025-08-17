"""Common utility types and aliases for Claude Monitor."""

from typing import NotRequired, TypedDict


# Type aliases for common patterns
JSONSerializable = (
    str
    | int
    | float
    | bool
    | None
    | dict[str, "JSONSerializable"]
    | list["JSONSerializable"]
)


class ErrorContext(TypedDict, total=False):
    """Context data for error reporting."""

    component: str
    operation: str
    file_path: NotRequired[str]
    session_id: NotRequired[str]
    additional_info: NotRequired[str]


class EntryData(TypedDict):
    """Processed entry data for cost calculation."""

    model: str
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cost_usd: float | None


class LimitInfo(TypedDict):
    """Information about detected usage limits."""

    timestamp: str  # Changed from datetime to match usage
    limit_type: str
    tokens_used: int
    message: str


class ProjectionData(TypedDict):
    """Projection data for session blocks."""

    projected_total_tokens: int
    projected_total_cost: float
    remaining_minutes: float


class ExtractedTokens(TypedDict):
    """Extracted token counts from Claude message data."""

    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int


class ExtractedMetadata(TypedDict):
    """Extracted metadata from Claude message entries."""

    message_id: str
    request_id: str