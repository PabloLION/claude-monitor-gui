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


class ErrorState(TypedDict, total=False):
    """Context data for error reporting."""

    component: str
    operation: str
    file_path: NotRequired[str]
    session_id: NotRequired[str]
    additional_info: NotRequired[str]


class ProcessedEntry(TypedDict):
    """Processed entry data for cost calculation."""

    model: str
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cost_usd: float | None


class LimitEvent(TypedDict):
    """Information about detected usage limits."""

    timestamp: str  # Changed from datetime to match usage
    limit_type: str
    tokens_used: int
    message: str


class SessionProjection(TypedDict):
    """Projection data for session blocks."""

    projected_total_tokens: int
    projected_total_cost: float
    remaining_minutes: float


class TokenExtract(TypedDict):
    """Extracted token counts from Claude message data."""

    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int


class MetadataExtract(TypedDict):
    """Extracted metadata from Claude message entries."""

    message_id: str
    request_id: str


class RawJSONEntry(TypedDict, total=False):
    """Type-safe structure for raw JSON data from JSONL files."""

    # Core fields that may be present in raw Claude data
    timestamp: NotRequired[str]
    message: NotRequired[dict[str, JSONSerializable]]
    request_id: NotRequired[str]
    type: NotRequired[str]
    model: NotRequired[str]
    usage: NotRequired[dict[str, JSONSerializable]]
    content: NotRequired[str]
    input_tokens: NotRequired[int]
    output_tokens: NotRequired[int]
    cache_creation_tokens: NotRequired[int]
    cache_read_tokens: NotRequired[int]
    # Allow additional unknown fields


class FlattenedEntry(TypedDict, total=False):
    """Type-safe structure for flattened data from data processors."""

    # All fields are optional since flattening can create various structures
    timestamp: NotRequired[str]
    model: NotRequired[str]
    input_tokens: NotRequired[int]
    output_tokens: NotRequired[int]
    cache_creation_tokens: NotRequired[int]
    cache_read_tokens: NotRequired[int]
    cost_usd: NotRequired[float]
    # Allow additional flattened fields


class NotificationValidation(TypedDict, total=False):
    """Type-safe structure for validation states in notifications."""

    # Common notification state fields
    switch_to_custom: NotRequired[bool]
    exceed_max_limit: NotRequired[bool]
    cost_will_exceed: NotRequired[bool]
    last_notified: NotRequired[str]  # Timestamp
    notification_count: NotRequired[int]


class TokenSourceData(TypedDict, total=False):
    """Type-safe structure for token source data from usage fields."""

    # Common token field variations found in Claude API responses
    input_tokens: NotRequired[int]
    output_tokens: NotRequired[int]
    cache_creation_tokens: NotRequired[int]
    cache_read_tokens: NotRequired[int]
    cache_creation_input_tokens: NotRequired[int]
    cache_read_input_tokens: NotRequired[int]

    # Alternative field names
    inputTokens: NotRequired[int]
    outputTokens: NotRequired[int]
    cacheCreationInputTokens: NotRequired[int]
    cacheReadInputTokens: NotRequired[int]
    prompt_tokens: NotRequired[int]
    completion_tokens: NotRequired[int]


class RawModelStats(TypedDict, total=False):
    """Type-safe structure for raw model statistics from API responses."""

    # Token counts (most common format)
    input_tokens: NotRequired[int]
    output_tokens: NotRequired[int]
    cache_creation_tokens: NotRequired[int]
    cache_read_tokens: NotRequired[int]

    # Additional cost and metadata fields that might be present
    cost: NotRequired[float]
    model_name: NotRequired[str]


class CallbackEventData(TypedDict):
    """Type-safe structure for monitoring callback data."""

    # Core monitoring fields that callbacks expect
    timestamp: str
    session_id: str | None
    token_usage: int
    cost: float
