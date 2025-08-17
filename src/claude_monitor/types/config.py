"""Configuration and settings types for Claude Monitor."""

from typing import TypedDict


class LastUsedParamsDict(TypedDict, total=False):
    """Type-safe structure for last used parameters."""

    plan: str
    view: str
    timezone: str
    theme: str
    time_format: str
    custom_limit_tokens: int
    refresh_rate: int
    refresh_per_second: float
    reset_hour: int
    debug: bool
    data_path: str
    timestamp: str  # Added for compatibility with existing code


class PlanLimitsEntry(TypedDict):
    """Typed structure for plan limit definitions."""
    
    token_limit: int
    cost_limit: float
    message_limit: int
    display_name: str