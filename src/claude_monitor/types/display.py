"""UI and display-related types for Claude Monitor."""

from datetime import datetime
from typing import NotRequired
from typing import TypedDict

from .common import JSONSerializable
from .sessions import ModelStats


class ModelStatsDisplay(TypedDict):
    """Token statistics for display purposes - simplified version."""

    input_tokens: int
    output_tokens: int
    cache_creation_tokens: NotRequired[int]
    cache_read_tokens: NotRequired[int]


class TimeData(TypedDict):
    """Time-related data for session calculations."""

    start_time: datetime | None
    reset_time: datetime | None
    minutes_to_reset: float
    total_session_minutes: float
    elapsed_session_minutes: float


class CostPredictions(TypedDict):
    """Cost-related predictions for session calculations."""

    cost_per_minute: float
    cost_limit: float
    cost_remaining: float
    predicted_end_time: datetime


class ExtractedSessionData(TypedDict):
    """Type-safe structure for extracted session data in display controller."""

    tokens_used: int
    session_cost: float
    raw_per_model_stats: dict[str, JSONSerializable]
    sent_messages: int
    entries: list[JSONSerializable]
    start_time_str: str | None
    end_time_str: str | None


class ProcessedDisplayData(TypedDict):
    """Type-safe structure for processed display data."""

    plan: str
    timezone: str
    tokens_used: int
    token_limit: int
    usage_percentage: float
    tokens_left: int
    elapsed_session_minutes: float
    total_session_minutes: float
    burn_rate: float
    session_cost: float
    per_model_stats: dict[str, ModelStats]
    model_distribution: dict[str, float]
    sent_messages: int
    entries: list[dict[str, JSONSerializable]]
    predicted_end_str: str
    reset_time_str: str
    current_time_str: str
    show_switch_notification: bool
    show_exceed_notification: bool
    show_tokens_will_run_out: bool
    original_limit: int
    cost_limit_p90: NotRequired[float]
    messages_limit_p90: NotRequired[int | float]


class ModelStatsDict(TypedDict, total=False):
    """Model statistics for progress bar display."""

    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    total_tokens: int
    cost_usd: float
    percentage: float


class ProgressBarStyleConfig(TypedDict, total=False):
    """Configuration for progress bar styling."""

    bar_width: int
    show_percentage: bool
    show_values: bool
    color_low: str
    color_medium: str
    color_high: str


class ThresholdConfig(TypedDict):
    """Threshold configuration for progress indicators."""

    low: float
    medium: float
    high: float


class NotificationFlags(TypedDict):
    """Notification flags for display controller."""

    show_switch_notification: bool
    show_exceed_notification: bool
    show_cost_will_exceed: bool


class DisplayTimes(TypedDict):
    """Formatted display times for UI."""

    predicted_end_str: str
    reset_time_str: str
    current_time_str: str


class VelocityIndicator(TypedDict):
    """Velocity indicator for burn rate visualization."""

    emoji: str
    label: str
