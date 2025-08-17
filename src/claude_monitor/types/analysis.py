"""Data analysis and aggregation types for Claude Monitor."""

from typing import NotRequired
from typing import TypedDict


class AggregatedData(TypedDict, total=False):
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


class AggregatedTotals(TypedDict):
    """Type-safe totals from aggregated data."""

    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    total_tokens: int
    total_cost: float
    entries_count: int


class SessionDataDict(TypedDict):
    """Type-safe structure for session data in UI components."""

    tokens: int
    cost: float
    messages: int


class SessionCollectionDict(TypedDict):
    """Type-safe structure for session collection results."""

    all_sessions: list[SessionDataDict]
    limit_sessions: list[SessionDataDict]
    current_session: SessionDataDict | None
    total_sessions: int
    active_sessions: int


class PercentileDict(TypedDict):
    """Type-safe structure for percentile calculations."""

    p50: int | float
    p75: int | float
    p90: int | float
    p95: int | float


class SessionPercentilesDict(TypedDict):
    """Type-safe structure for session percentiles results."""

    tokens: PercentileDict
    costs: PercentileDict
    messages: PercentileDict
    averages: dict[str, int | float]
    count: int


class AggregatedStats(TypedDict):
    """Aggregated statistics from data aggregator to_dict method."""

    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cost: float
    count: int
