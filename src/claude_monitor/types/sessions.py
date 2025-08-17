"""Session and block data types for Claude Monitor."""

from datetime import datetime
from typing import NotRequired, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from .api import ClaudeJSONEntry


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


class FormattedLimitInfo(TypedDict):
    """Formatted limit info for JSON output."""

    type: str
    timestamp: str
    content: str
    reset_time: str | None


class LimitDetectionInfo(TypedDict):
    """Raw limit detection info from analyzer."""

    type: str
    timestamp: datetime
    content: str
    reset_time: NotRequired[datetime]
    wait_minutes: NotRequired[float]
    raw_data: NotRequired["ClaudeJSONEntry"]
    block_context: NotRequired[dict[str, str | int]]


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


class ModelStats(TypedDict):
    """Statistics for a specific model's usage."""

    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cost_usd: float
    entries_count: int


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


class SessionData(TypedDict):
    """Data for session monitoring."""

    session_id: str
    block_data: BlockDict
    is_new: bool
    timestamp: datetime


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


class AnalysisResult(TypedDict):
    """Result from analyze_usage function."""

    blocks: list[BlockDict]
    metadata: AnalysisMetadata
    entries_count: int
    total_tokens: int
    total_cost: float


class MonitoringData(TypedDict):
    """Data from monitoring orchestrator."""

    data: AnalysisResult
    token_limit: int
    args: object  # argparse.Namespace
    session_id: str | None
    session_count: int