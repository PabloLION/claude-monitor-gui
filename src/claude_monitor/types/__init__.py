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
from .api import *
from .sessions import *
from .display import *
from .config import *
from .analysis import *
from .common import *

__all__ = [
    # API types
    "SystemEntry",
    "UserEntry", 
    "AssistantEntry",
    "ClaudeJSONEntry",
    "TokenUsage",
    
    # Session types
    "BlockDict",
    "BlockData", 
    "SessionData",
    "AnalysisResult",
    "BlockEntry",
    "FormattedLimitInfo",
    "LimitDetectionInfo",
    
    # Display types
    "ExtractedSessionData",
    "ProcessedDisplayData",
    "TimeData",
    "CostPredictions",
    "ModelStatsDict",
    "ProgressBarStyleConfig",
    "ThresholdConfig",
    "NotificationFlags",
    "DisplayTimes",
    
    # Config types
    "LastUsedParamsDict",
    "PlanLimitsEntry",
    
    # Analysis types
    "AnalysisMetadata",
    "AggregatedData",
    "AggregatedTotals",
    "ModelStats",
    "SessionDataDict",
    "SessionCollectionDict",
    "PercentileDict",
    "SessionPercentilesDict",
    
    # Common types
    "JSONSerializable",
    "ErrorContext",
    "EntryData",
    "TokenCountsDict",
    "BurnRateDict", 
    "ProjectionDict",
    "ProjectionData",
    "LimitInfo",
    "MonitoringData",
    "ExtractedTokens",
    "ExtractedMetadata",
]