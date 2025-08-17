"""Centralized data processing utilities for Claude Monitor.

This module provides unified data processing functionality to eliminate
code duplication across different components.
"""

from datetime import datetime
from typing import cast

from claude_monitor.types import ClaudeJSONEntry
from claude_monitor.types import ExtractedTokens
from claude_monitor.types import JSONSerializable
from claude_monitor.utils.time_utils import TimezoneHandler


class TimestampProcessor:
    """Unified timestamp parsing and processing utilities."""

    def __init__(self, timezone_handler: TimezoneHandler | None = None) -> None:
        """Initialize with optional timezone handler."""
        self.timezone_handler: TimezoneHandler = timezone_handler or TimezoneHandler()

    def parse_timestamp(
        self, timestamp_value: str | int | float | datetime | None
    ) -> datetime | None:
        """Parse timestamp from various formats to UTC datetime.

        Args:
            timestamp_value: Timestamp in various formats (str, int, float, datetime)

        Returns:
            Parsed UTC datetime or None if parsing fails
        """
        if timestamp_value is None:
            return None

        try:
            if isinstance(timestamp_value, datetime):
                return self.timezone_handler.ensure_timezone(timestamp_value)

            if isinstance(timestamp_value, str):
                if timestamp_value.endswith("Z"):
                    timestamp_value = timestamp_value[:-1] + "+00:00"

                try:
                    dt = datetime.fromisoformat(timestamp_value)
                    return self.timezone_handler.ensure_timezone(dt)
                except ValueError:
                    pass

                for fmt in ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]:
                    try:
                        dt = datetime.strptime(timestamp_value, fmt)
                        return self.timezone_handler.ensure_timezone(dt)
                    except ValueError:
                        continue

            if isinstance(timestamp_value, (int, float)):
                dt = datetime.fromtimestamp(timestamp_value)
                return self.timezone_handler.ensure_timezone(dt)

        except Exception:
            pass

        return None


class TokenExtractor:
    """Unified token extraction utilities."""

    @staticmethod
    def extract_tokens(data: ClaudeJSONEntry) -> ExtractedTokens:
        """Extract token counts from data in standardized format.

        Args:
            data: Claude message entry with token information

        Returns:
            Dictionary with standardized token keys and counts
        """
        import logging

        logger = logging.getLogger(__name__)

        tokens: dict[str, int] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_creation_tokens": 0,
            "cache_read_tokens": 0,
            "total_tokens": 0,
        }

        # Define token extraction helper
        def safe_get_int(value: JSONSerializable | None) -> int:
            """Safely convert value to int.

            Args:
                value: Value from API response (int, float, str, or None)

            Returns:
                int: Converted value or 0 if conversion fails
            """
            if isinstance(value, (int, float)):
                return int(value)
            elif isinstance(value, str):
                try:
                    # Try to parse string numbers (common in API responses)
                    return int(float(value))
                except (ValueError, TypeError):
                    return 0
            return 0

        # Handle new specific types with type narrowing
        if isinstance(data, dict) and "type" in data:
            entry_type = data.get("type")
            if entry_type == "system" or entry_type == "user":
                # System and user messages don't have token usage
                logger.debug("TokenExtractor: System/user messages have no token usage")
                return {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cache_creation_tokens": 0,
                    "cache_read_tokens": 0,
                }
            elif entry_type == "assistant":
                # Assistant messages have token usage - proceed with extraction
                pass

        # Build token sources - these are dicts that might contain token info
        token_sources: list[dict[str, JSONSerializable]] = []

        # Build token sources in priority order
        is_assistant: bool = data.get("type") == "assistant"

        if is_assistant:
            # Assistant message: check message.usage first, then usage, then top-level
            if message := data.get("message"):
                if isinstance(message, dict) and (usage := message.get("usage")):
                    if isinstance(usage, dict):
                        # Cast to ensure type compatibility - dict values are compatible with JSONSerializable
                        token_sources.append(usage)

            if usage := data.get("usage"):
                if isinstance(usage, dict):
                    # Cast to ensure type compatibility - dict values are compatible with JSONSerializable
                    token_sources.append(usage)

            # Top-level fields as fallback (cast for type compatibility)
            token_sources.append(cast(dict[str, JSONSerializable], data))
        else:
            # User message: check usage first, then message.usage, then top-level
            if usage := data.get("usage"):
                if isinstance(usage, dict):
                    # Cast to ensure type compatibility - dict values are compatible with JSONSerializable
                    token_sources.append(usage)

            if message := data.get("message"):
                if isinstance(message, dict) and (usage := message.get("usage")):
                    if isinstance(usage, dict):
                        # Cast to ensure type compatibility - dict values are compatible with JSONSerializable
                        token_sources.append(usage)

            # Top-level fields as fallback (cast for type compatibility)
            token_sources.append(cast(dict[str, JSONSerializable], data))

        logger.debug(f"TokenExtractor: Checking {len(token_sources)} token sources")

        # Extract tokens from first valid source
        for source in token_sources:
            # Try multiple field name variations
            input_tokens = (
                safe_get_int(source.get("input_tokens"))
                or safe_get_int(source.get("inputTokens"))
                or safe_get_int(source.get("prompt_tokens"))
            )

            output_tokens = (
                safe_get_int(source.get("output_tokens"))
                or safe_get_int(source.get("outputTokens"))
                or safe_get_int(source.get("completion_tokens"))
            )

            cache_creation = (
                safe_get_int(source.get("cache_creation_tokens"))
                or safe_get_int(source.get("cache_creation_input_tokens"))
                or safe_get_int(source.get("cacheCreationInputTokens"))
            )

            cache_read = (
                safe_get_int(source.get("cache_read_input_tokens"))
                or safe_get_int(source.get("cache_read_tokens"))
                or safe_get_int(source.get("cacheReadInputTokens"))
            )

            if input_tokens > 0 or output_tokens > 0:
                tokens.update(
                    {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cache_creation_tokens": cache_creation,
                        "cache_read_tokens": cache_read,
                        "total_tokens": input_tokens
                        + output_tokens
                        + cache_creation
                        + cache_read,
                    }
                )
                logger.debug(
                    f"TokenExtractor: Found tokens - input={input_tokens}, output={output_tokens}, cache_creation={cache_creation}, cache_read={cache_read}"
                )
                break

            logger.debug("TokenExtractor: No valid tokens in source")

        if tokens["total_tokens"] == 0:
            logger.debug("TokenExtractor: No tokens found in any source")

        return {
            "input_tokens": tokens["input_tokens"],
            "output_tokens": tokens["output_tokens"],
            "cache_creation_tokens": tokens["cache_creation_tokens"],
            "cache_read_tokens": tokens["cache_read_tokens"],
        }


class DataConverter:
    """Unified data conversion utilities."""

    @staticmethod
    def flatten_nested_dict(
        data: dict[str, JSONSerializable], prefix: str = ""
    ) -> dict[str, JSONSerializable]:
        """Flatten nested dictionary structure.

        Args:
            data: Nested dictionary
            prefix: Prefix for flattened keys

        Returns:
            Flattened dictionary
        """
        result: dict[str, JSONSerializable] = {}

        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                result.update(DataConverter.flatten_nested_dict(value, new_key))
            else:
                result[new_key] = value

        return result

    @staticmethod
    def extract_model_name(
        data: ClaudeJSONEntry, default: str = "claude-3-5-sonnet"
    ) -> str:
        """Extract model name from various data sources.

        Args:
            data: Claude message entry containing model information
            default: Default model name if not found

        Returns:
            Extracted model name
        """
        # Check model in priority order with TypedDict fields
        model_candidates: list[str | None] = [
            (
                cast(str, data.get("model"))
                if isinstance(data.get("model"), str)
                else None
            ),  # Direct model field
            None,
        ]

        # Check nested message.model
        if message := data.get("message"):
            if message and isinstance(message, dict):
                model = message.get("model")
                if isinstance(model, str):
                    model_candidates.insert(0, model)

        # Check nested usage.model
        if usage := data.get("usage"):
            if usage and isinstance(usage, dict):
                # Cast to dict to handle additional fields not in TokenUsage
                usage_dict = dict(usage)
                model = usage_dict.get("model")
                if isinstance(model, str):
                    model_candidates.append(model)

        for candidate in model_candidates:
            if candidate:
                return candidate

        return default

    @staticmethod
    def to_serializable(obj: JSONSerializable) -> JSONSerializable:
        """Convert object to JSON-serializable format.

        Args:
            obj: Object to convert

        Returns:
            JSON-serializable representation
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {k: DataConverter.to_serializable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [DataConverter.to_serializable(item) for item in obj]
        return obj
