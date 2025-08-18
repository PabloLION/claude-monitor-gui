"""Session and block data types for Claude Monitor."""

from datetime import datetime
from typing import TYPE_CHECKING
from typing import NotRequired
from typing import Required
from typing import TypedDict


if TYPE_CHECKING:
    from .api import ClaudeMessageEntry


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


class LimitDetectionInfo(TypedDict, total=False):
    """Raw limit detection info from analyzer."""

    type: Required[str]
    timestamp: Required[datetime]
    content: Required[str]
    reset_time: NotRequired[datetime]
    wait_minutes: NotRequired[float]
    raw_data: NotRequired["ClaudeMessageEntry"]
    block_context: NotRequired[dict[str, str | int]]


class TokenCountsData(TypedDict):
    """Token counts dictionary for JSON output."""

    inputTokens: int
    outputTokens: int
    cacheCreationInputTokens: int
    cacheReadInputTokens: int


class BurnRateData(TypedDict):
    """Burn rate dictionary for JSON output."""

    tokensPerMinute: float
    costPerHour: float


class SessionProjectionJson(TypedDict):
    """Projection data dictionary for JSON output."""

    totalTokens: int
    totalCost: float
    remainingMinutes: float


class ModelUsageStats(TypedDict):
    """Statistics for a specific model's usage."""

    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cost_usd: float
    entries_count: int


class SerializedBlock(TypedDict):
    """Serialized SessionBlock for JSON output."""

    id: str
    isActive: bool
    isGap: bool
    startTime: str
    endTime: str
    actualEndTime: str | None
    tokenCounts: TokenCountsData
    totalTokens: int
    costUSD: float
    models: list[str]
    perModelStats: dict[str, ModelUsageStats]
    sentMessagesCount: int
    durationMinutes: float
    entries: list[BlockEntry]
    entries_count: int
    burnRate: NotRequired[BurnRateData]
    projection: NotRequired[SessionProjectionJson]
    limitMessages: NotRequired[list[FormattedLimitInfo]]


class PartialBlock(TypedDict, total=False):
    """Partial block data - same fields as BlockDict but all optional."""

    id: str
    isActive: bool
    isGap: bool
    startTime: str
    endTime: str
    actualEndTime: str | None
    tokenCounts: TokenCountsData
    totalTokens: int
    costUSD: float
    models: list[str]
    perModelStats: dict[str, ModelUsageStats]
    sentMessagesCount: int
    durationMinutes: float
    entries: list[BlockEntry]
    entries_count: int
    burnRate: BurnRateData
    projection: SessionProjectionJson
    limitMessages: list[FormattedLimitInfo]


# BlockData now uses the partial format - will be renamed in future commit
LegacyBlockData = PartialBlock


class SessionBlockMonitoringData(TypedDict):
    """Data for session monitoring with block information."""

    session_id: str
    block_data: SerializedBlock
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

    blocks: list[SerializedBlock]
    metadata: AnalysisMetadata
    entries_count: int
    total_tokens: int
    total_cost: float


class MonitoringState(TypedDict):
    """Data from monitoring orchestrator."""

    data: AnalysisResult
    token_limit: int
    args: object  # argparse.Namespace
    session_id: str | None
    session_count: int
