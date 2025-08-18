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


class RawJSONData(TypedDict, total=False):
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


class FlattenedData(TypedDict, total=False):
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


class ValidationState(TypedDict, total=False):
    """Type-safe structure for validation states in notifications."""

    # Common notification state fields
    switch_to_custom: NotRequired[bool]
    exceed_max_limit: NotRequired[bool]
    cost_will_exceed: NotRequired[bool]
    last_notified: NotRequired[str]  # Timestamp
    notification_count: NotRequired[int]


class MonitoringCallbackData(TypedDict):
    """Type-safe structure for monitoring callback data."""

    # Core monitoring fields that callbacks expect
    timestamp: str
    session_id: str | None
    token_usage: int
    cost: float
