"""Centralized data processing utilities for Claude Monitor.

This module provides unified data processing functionality to eliminate
code duplication across different components.
"""

from datetime import datetime
from claude_monitor.core.models import JSONSerializable

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
    def extract_tokens(data: dict[str, JSONSerializable]) -> dict[str, int]:
        """Extract token counts from data in standardized format.

        Args:
            data: Data dictionary with token information

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

        token_sources: list[dict[str, JSONSerializable]] = []

        is_assistant: bool = data.get("type") == "assistant"

        if is_assistant:
            if (
                "message" in data
                and isinstance(data["message"], dict)
                and "usage" in data["message"]
                and isinstance(data["message"]["usage"], dict)
            ):
                token_sources.append(data["message"]["usage"])
            if "usage" in data and isinstance(data["usage"], dict):
                token_sources.append(data["usage"])
            token_sources.append(data)
        else:
            if "usage" in data and isinstance(data["usage"], dict):
                token_sources.append(data["usage"])
            if (
                "message" in data
                and isinstance(data["message"], dict)
                and "usage" in data["message"]
                and isinstance(data["message"]["usage"], dict)
            ):
                token_sources.append(data["message"]["usage"])
            token_sources.append(data)

        logger.debug(f"TokenExtractor: Checking {len(token_sources)} token sources")

        for source in token_sources:
            if not isinstance(source, dict):
                continue

            def safe_get_numeric(source: dict[str, JSONSerializable], key: str, default: int = 0) -> int:
                """Safely extract numeric value from JSONSerializable dict."""
                value = source.get(key, default)
                if isinstance(value, (int, float)):
                    return int(value)
                return default

            input_tokens = (
                safe_get_numeric(source, "input_tokens")
                or safe_get_numeric(source, "inputTokens")
                or safe_get_numeric(source, "prompt_tokens")
                or 0
            )

            output_tokens = (
                safe_get_numeric(source, "output_tokens")
                or safe_get_numeric(source, "outputTokens")
                or safe_get_numeric(source, "completion_tokens")
                or 0
            )

            cache_creation = (
                safe_get_numeric(source, "cache_creation_tokens")
                or safe_get_numeric(source, "cache_creation_input_tokens")
                or safe_get_numeric(source, "cacheCreationInputTokens")
                or 0
            )

            cache_read = (
                safe_get_numeric(source, "cache_read_input_tokens")
                or safe_get_numeric(source, "cache_read_tokens")
                or safe_get_numeric(source, "cacheReadInputTokens")
                or 0
            )

            if input_tokens > 0 or output_tokens > 0:
                tokens.update(
                    {
                        "input_tokens": int(input_tokens),
                        "output_tokens": int(output_tokens),
                        "cache_creation_tokens": int(cache_creation),
                        "cache_read_tokens": int(cache_read),
                        "total_tokens": int(
                            input_tokens + output_tokens + cache_creation + cache_read
                        ),
                    }
                )
                logger.debug(
                    f"TokenExtractor: Found tokens - input={input_tokens}, output={output_tokens}, cache_creation={cache_creation}, cache_read={cache_read}"
                )
                break
            logger.debug(
                f"TokenExtractor: No valid tokens in source: {list(source.keys()) if isinstance(source, dict) else 'not a dict'}"
            )

        return tokens


class DataConverter:
    """Unified data conversion utilities."""

    @staticmethod
    def flatten_nested_dict(data: dict[str, JSONSerializable], prefix: str = "") -> dict[str, JSONSerializable]:
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
        data: dict[str, JSONSerializable], default: str = "claude-3-5-sonnet"
    ) -> str:
        """Extract model name from various data sources.

        Args:
            data: Data containing model information
            default: Default model name if not found

        Returns:
            Extracted model name
        """
        def safe_get_nested(data: dict[str, JSONSerializable], outer_key: str, inner_key: str) -> JSONSerializable | None:
            """Safely get nested value from dict."""
            outer_value = data.get(outer_key)
            if isinstance(outer_value, dict):
                return outer_value.get(inner_key)
            return None

        model_candidates: list[JSONSerializable | None] = [
            safe_get_nested(data, "message", "model"),
            data.get("model"),
            data.get("Model"),
            safe_get_nested(data, "usage", "model"),
            safe_get_nested(data, "request", "model"),
        ]

        for candidate in model_candidates:
            if candidate and isinstance(candidate, str):
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
