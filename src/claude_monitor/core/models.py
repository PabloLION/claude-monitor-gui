"""Data models for Claude Monitor.
Core data structures for usage tracking, session management, and token calculations.
"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import NotRequired
from typing import TypedDict


class CostMode(Enum):
    """Cost calculation modes for token usage analysis."""

    AUTO = "auto"
    CACHED = "cached"
    CALCULATED = "calculate"


@dataclass
class UsageEntry:
    """Individual usage record from Claude usage data."""

    timestamp: datetime
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    cost_usd: float = 0.0
    model: str = ""
    message_id: str = ""
    request_id: str = ""


@dataclass
class TokenCounts:
    """Token aggregation structure with computed totals."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Get total tokens across all types."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_tokens
            + self.cache_read_tokens
        )


@dataclass
class BurnRate:
    """Token consumption rate metrics."""

    tokens_per_minute: float
    cost_per_hour: float


@dataclass
class UsageProjection:
    """Usage projection calculations for active blocks."""

    projected_total_tokens: int
    projected_total_cost: float
    remaining_minutes: float


# TypedDict classes needed by dataclasses
class ModelStats(TypedDict):
    """Statistics for a specific model's usage."""

    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cost_usd: float
    entries_count: int


class LimitInfo(TypedDict):
    """Information about detected usage limits."""

    timestamp: datetime
    limit_type: str
    tokens_used: int
    message: str


class ProjectionData(TypedDict):
    """Projection data for session blocks."""

    projected_total_tokens: int
    projected_total_cost: float
    remaining_minutes: float


@dataclass
class SessionBlock:
    """Aggregated session block representing a 5-hour period."""

    id: str
    start_time: datetime
    end_time: datetime
    entries: list[UsageEntry] = field(default_factory=list)
    token_counts: TokenCounts = field(default_factory=TokenCounts)
    is_active: bool = False
    is_gap: bool = False
    burn_rate: BurnRate | None = None
    actual_end_time: datetime | None = None
    per_model_stats: dict[str, ModelStats] = field(default_factory=dict)
    models: list[str] = field(default_factory=list)
    sent_messages_count: int = 0
    cost_usd: float = 0.0
    limit_messages: list[LimitInfo] = field(default_factory=list)
    projection_data: ProjectionData | None = None
    burn_rate_snapshot: BurnRate | None = None

    @property
    def total_tokens(self) -> int:
        """Get total tokens from token_counts."""
        return self.token_counts.total_tokens

    @property
    def total_cost(self) -> float:
        """Get total cost - alias for cost_usd."""
        return self.cost_usd

    @property
    def duration_minutes(self) -> float:
        """Get duration in minutes."""
        if self.actual_end_time:
            duration = (
                self.actual_end_time - self.start_time
            ).total_seconds() / 60
        else:
            duration = (self.end_time - self.start_time).total_seconds() / 60
        return max(duration, 1.0)


def normalize_model_name(model: str) -> str:
    """Normalize model name for consistent usage across the application.

    Handles various model name formats and maps them to standard keys.
    (Moved from utils/model_utils.py)

    Args:
        model: Raw model name from usage data

    Returns:
        Normalized model key

    Examples:
        >>> normalize_model_name("claude-3-opus-20240229")
        'claude-3-opus'
        >>> normalize_model_name("Claude 3.5 Sonnet")
        'claude-3-5-sonnet'
    """
    if not model:
        return ""

    model_lower = model.lower()

    if (
        "claude-opus-4-" in model_lower
        or "claude-sonnet-4-" in model_lower
        or "claude-haiku-4-" in model_lower
        or "sonnet-4-" in model_lower
        or "opus-4-" in model_lower
        or "haiku-4-" in model_lower
    ):
        return model_lower

    if "opus" in model_lower:
        if "4-" in model_lower:
            return model_lower
        return "claude-3-opus"
    if "sonnet" in model_lower:
        if "4-" in model_lower:
            return model_lower
        if "3.5" in model_lower or "3-5" in model_lower:
            return "claude-3-5-sonnet"
        return "claude-3-sonnet"
    if "haiku" in model_lower:
        if "3.5" in model_lower or "3-5" in model_lower:
            return "claude-3-5-haiku"
        return "claude-3-haiku"

    return model


class RawJSONEntry(TypedDict, total=False):
    """Raw JSONL entry from Claude usage data files."""

    timestamp: str
    message_id: NotRequired[str]
    request_id: NotRequired[str]
    requestId: NotRequired[str]  # Alternative field name
    message: NotRequired[dict[str, str | int]]
    cost: NotRequired[float]
    cost_usd: NotRequired[float]
    model: NotRequired[str]
    # Token usage fields
    usage: NotRequired[dict[str, int]]
    input_tokens: NotRequired[int]
    output_tokens: NotRequired[int]
    cache_creation_tokens: NotRequired[int]
    cache_read_tokens: NotRequired[int]


class EntryData(TypedDict):
    """Processed entry data for cost calculation."""

    model: str
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cost_usd: float | None


class TokenCountsDict(TypedDict):
    """Token counts dictionary for JSON output."""

    inputTokens: int
    outputTokens: int
    cacheCreationInputTokens: int
    cacheReadInputTokens: int


class BurnRateDict(TypedDict):
    """Burn rate dictionary for JSON output."""

    tokensPerMinute: float
    costPerHour: float


class ProjectionDict(TypedDict):
    """Projection data dictionary for JSON output."""

    totalTokens: int
    totalCost: float
    remainingMinutes: float


class LimitDetectionInfo(TypedDict):
    """Raw limit detection info from analyzer."""

    type: str
    timestamp: datetime
    content: str
    reset_time: NotRequired[datetime]
    wait_minutes: NotRequired[float]
    raw_data: NotRequired[dict[str, str | int | float]]
    block_context: NotRequired[dict[str, str | int | float]]


class FormattedLimitInfo(TypedDict):
    """Formatted limit info for JSON output."""

    type: str
    timestamp: str
    content: str
    reset_time: str | None


class BlockEntry(TypedDict):
    """Formatted usage entry for JSON output."""

    timestamp: str
    inputTokens: int
    outputTokens: int
    cacheCreationTokens: int
    cacheReadInputTokens: int
    costUSD: float
    model: str
    messageId: str
    requestId: str


class AnalysisMetadata(TypedDict):
    """Metadata from usage analysis."""

    generated_at: str
    hours_analyzed: int | str
    entries_processed: int
    blocks_created: int
    limits_detected: int
    load_time_seconds: float
    transform_time_seconds: float
    cache_used: bool
    quick_start: bool


class BlockDict(TypedDict):
    """Serialized SessionBlock for JSON output."""

    id: str
    isActive: bool
    isGap: bool
    startTime: str
    endTime: str
    actualEndTime: str | None
    tokenCounts: TokenCountsDict
    totalTokens: int
    costUSD: float
    models: list[str]
    perModelStats: dict[str, ModelStats]
    sentMessagesCount: int
    durationMinutes: float
    entries: list[BlockEntry]
    entries_count: int
    burnRate: NotRequired[BurnRateDict]
    projection: NotRequired[ProjectionDict]
    limitMessages: NotRequired[list[FormattedLimitInfo]]


class AnalysisResult(TypedDict):
    """Result from analyze_usage function."""

    blocks: list[BlockDict]
    metadata: AnalysisMetadata
    entries_count: int
    total_tokens: int
    total_cost: float


class SessionData(TypedDict):
    """Data for session monitoring."""

    session_id: str
    block_data: BlockDict
    is_new: bool
    timestamp: datetime


class MonitoringData(TypedDict):
    """Data from monitoring orchestrator."""

    data: AnalysisResult
    token_limit: int
    args: object  # argparse.Namespace
    session_id: str | None
    session_count: int


# TypedDict for block data from session analysis
class BlockData(TypedDict, total=False):
    """Block data from Claude session analysis."""
    
    # Required fields
    id: str
    isActive: bool
    isGap: bool
    totalTokens: int
    startTime: str
    endTime: str
    costUSD: float
    
    # Optional fields
    actualEndTime: str
    tokenCounts: dict[str, int]
    models: list[str]
    perModelStats: dict[str, dict[str, int | float]]
    sentMessagesCount: int
    durationMinutes: float
    entries: list[dict[str, str | int | float]]
    entries_count: int
    burnRate: dict[str, float]
    projection: dict[str, int | float]
    limitMessages: list[dict[str, str]]


# TypedDict for token usage data
class TokenUsage(TypedDict, total=False):
    """Token usage information from various sources."""
    
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cache_creation_input_tokens: int  # Alternative field name
    cache_read_input_tokens: int      # Alternative field name
    inputTokens: int                  # Alternative field name (camelCase)
    outputTokens: int                 # Alternative field name (camelCase)
    cacheCreationInputTokens: int     # Alternative field name (camelCase)
    cacheReadInputTokens: int         # Alternative field name (camelCase)
    prompt_tokens: int                # Alternative field name (OpenAI format)
    completion_tokens: int            # Alternative field name (OpenAI format)
    total_tokens: int


# TypedDict for usage data from JSONL files
class UsageData(TypedDict, total=False):
    """Raw usage data from Claude JSONL files."""
    
    # Core fields
    timestamp: str
    type: str
    model: str
    
    # Token usage (various formats)
    usage: TokenUsage
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    
    # Message data
    message: dict[str, str | int | TokenUsage]
    message_id: str
    request_id: str
    requestId: str  # Alternative field name
    
    # Cost data
    cost: float
    cost_usd: float
    
    # Any other fields from JSON
    content: str | list[dict[str, str]]
    role: str


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
