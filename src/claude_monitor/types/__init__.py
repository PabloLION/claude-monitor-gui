"""Type definitions for Claude Monitor.

This package contains all TypedDict definitions organized by domain:
- api: Claude API message types
- sessions: Session and block data types
- display: UI and display-related types
- config: Configuration and settings types
- analysis: Data analysis and aggregation types
- common: Common utility types and aliases
"""

# Import all types for convenient access
from .analysis import *
from .api import *
from .common import *
from .config import *
from .display import *
from .sessions import *

__all__ = [
    # API types
    "SystemMessageEntry",
    "UserMessageEntry",
    "AssistantMessageEntry",
    "ClaudeMessageEntry",
    "TokenUsageData",
    # Session types
    "SerializedBlock",
    "LegacyBlockData",
    "AnalysisResult",
    "BlockEntry",
    "FormattedLimitInfo",
    "LimitDetectionInfo",
    # Display types
    "SessionDataExtract",
    "DisplayState",
    "TimeData",
    "CostPredictions",
    "ModelStatsDisplay",
    "ProgressBarStyle",
    "ThresholdConfig",
    "NotificationState",
    "FormattedTimes",
    "VelocityIndicator",
    # Config types
    "UserPreferences",
    "PlanConfiguration",
    # Analysis types
    "AnalysisMetadata",
    "AggregatedUsage",
    "CompleteAggregatedUsage",
    "UsageTotals",
    "ModelUsageStats",
    "SessionMonitoringData",
    "SessionCollection",
    "Percentiles",
    "SessionPercentiles",
    "UsageStatistics",
    # Common types
    "JSONSerializable",
    "ErrorState",
    "ProcessedEntry",
    "TokenCountsData",
    "BurnRateData",
    "SessionProjection",
    "SessionProjectionJson",
    "LimitEvent",
    "MonitoringState",
    "TokenExtract",
    "MetadataExtract",
    "RawJSONEntry",
    "FlattenedEntry",
    "NotificationValidation",
    "TokenSourceData",
    "RawModelStats",
    "CallbackEventData",
]
