"""Type definitions for Claude Monitor.

This package contains all TypedDict definitions organized by domain:
- api: Claude API message types
- sessions: Session and block data types
- display: UI and display-related types
- config: Configuration and settings types
- analysis: Data analysis and aggregation types
- common: Common utility types and aliases
"""

# ruff: noqa: I001
# Note: Import formatting disabled to preserve logical grouping

# Analysis types
from .analysis import (
    AggregatedUsage as AggregatedUsage,
    CompleteAggregatedUsage as CompleteAggregatedUsage,
    Percentiles as Percentiles,
    SessionCollection as SessionCollection,
    SessionMonitoringData as SessionMonitoringData,
    SessionPercentiles as SessionPercentiles,
    UsageStatistics as UsageStatistics,
    UsageTotals as UsageTotals,
)

# API types
from .api import (
    AssistantMessage as AssistantMessage,
    AssistantMessageEntry as AssistantMessageEntry,
    BaseClaudeEntry as BaseClaudeEntry,
    BaseMessageContent as BaseMessageContent,
    ClaudeMessageEntry as ClaudeMessageEntry,
    SystemMessage as SystemMessage,
    SystemMessageEntry as SystemMessageEntry,
    TokenUsageData as TokenUsageData,
    UserMessage as UserMessage,
    UserMessageEntry as UserMessageEntry,
)

# Common types
from .common import (
    CallbackEventData as CallbackEventData,
    ErrorState as ErrorState,
    FlattenedEntry as FlattenedEntry,
    JSONSerializable as JSONSerializable,
    LimitEvent as LimitEvent,
    MetadataExtract as MetadataExtract,
    NotificationValidation as NotificationValidation,
    ProcessedEntry as ProcessedEntry,
    RawJSONEntry as RawJSONEntry,
    RawModelStats as RawModelStats,
    SessionProjection as SessionProjection,
    TokenExtract as TokenExtract,
    TokenSourceData as TokenSourceData,
)

# Config types
from .config import (
    PlanConfiguration as PlanConfiguration,
    UserPreferences as UserPreferences,
)

# Display types
from .display import (
    CostPredictions as CostPredictions,
    DisplayModelStats as DisplayModelStats,
    DisplayState as DisplayState,
    FormattedTimes as FormattedTimes,
    ModelStatsDisplay as ModelStatsDisplay,
    NotificationState as NotificationState,
    ProgressBarStyle as ProgressBarStyle,
    SessionDataExtract as SessionDataExtract,
    ThresholdConfig as ThresholdConfig,
    TimeData as TimeData,
    VelocityIndicator as VelocityIndicator,
)

# Session types
from .sessions import (
    AnalysisMetadata as AnalysisMetadata,
    AnalysisResult as AnalysisResult,
    BlockEntry as BlockEntry,
    BurnRateData as BurnRateData,
    FormattedLimitInfo as FormattedLimitInfo,
    LegacyBlockData as LegacyBlockData,
    LimitDetectionInfo as LimitDetectionInfo,
    ModelUsageStats as ModelUsageStats,
    MonitoringState as MonitoringState,
    PartialBlock as PartialBlock,
    SerializedBlock as SerializedBlock,
    SessionBlockMonitoringData as SessionBlockMonitoringData,
    SessionProjectionJson as SessionProjectionJson,
    TokenCountsData as TokenCountsData,
)

# Explicit imports automatically define what's exported.
# No need for __all__ when we control exactly what we import.
