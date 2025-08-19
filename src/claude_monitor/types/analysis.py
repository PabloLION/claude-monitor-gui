"""Data analysis and aggregation types for Claude Monitor."""

from typing import NotRequired, Required, TypedDict


class AggregatedUsage(TypedDict, total=False):
    """Type-safe aggregated data for daily/monthly statistics."""

    # Period identifiers (one of these will be present)
    date: NotRequired[str]  # For daily aggregation (YYYY-MM-DD)
    month: NotRequired[str]  # For monthly aggregation (YYYY-MM)

    # Token statistics
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int

    # Cost and count
    total_cost: float
    entries_count: int

    # Model information
    models_used: list[str]
    model_breakdowns: dict[str, dict[str, int | float]]


class CompleteAggregatedUsage(TypedDict, total=False):
    """Type-safe aggregated data where all fields are confirmed/required."""

    # Period identifiers (one of these will be present)
    date: NotRequired[str]  # For daily aggregation (YYYY-MM-DD)
    month: NotRequired[str]  # For monthly aggregation (YYYY-MM)

    # Token statistics (all required)
    input_tokens: Required[int]
    output_tokens: Required[int]
    cache_creation_tokens: Required[int]
    cache_read_tokens: Required[int]

    # Cost and count (all required)
    total_cost: Required[float]
    entries_count: Required[int]

    # Model information (all required)
    models_used: Required[list[str]]
    model_breakdowns: Required[dict[str, dict[str, int | float]]]


class UsageTotals(TypedDict):
    """Type-safe totals from aggregated data."""

    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    total_tokens: int
    total_cost: float
    entries_count: int


class SessionMonitoringData(TypedDict):
    """Type-safe structure for session data in UI components."""

    tokens: int
    cost: float
    messages: int


class SessionCollection(TypedDict):
    """Type-safe structure for session collection results."""

    all_sessions: list[SessionMonitoringData]
    limit_sessions: list[SessionMonitoringData]
    current_session: SessionMonitoringData | None
    total_sessions: int
    active_sessions: int


class Percentiles(TypedDict):
    """Type-safe structure for percentile calculations."""

    p50: int | float
    p75: int | float
    p90: int | float
    p95: int | float


class SessionPercentiles(TypedDict):
    """Type-safe structure for session percentiles results."""

    tokens: Percentiles
    costs: Percentiles
    messages: Percentiles
    averages: dict[str, int | float]
    count: int


class UsageStatistics(TypedDict):
    """Aggregated statistics from data aggregator to_dict method."""

    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cost: float
    count: int
