"""Simplified data reader for Claude Monitor.

Combines functionality from file_reader, filter, mapper, and processor
into a single cohesive module.
"""

import json
import logging
from datetime import datetime, timedelta
from datetime import timezone as tz
from pathlib import Path

from claude_monitor.core.data_processors import (
    DataConverter,
    TimestampProcessor,
    TokenExtractor,
)
from claude_monitor.core.models import CostMode, UsageEntry
from claude_monitor.core.pricing import PricingCalculator
from claude_monitor.error_handling import report_file_error
from claude_monitor.types import (
    AssistantMessageEntry,
    ClaudeMessageEntry,
    MetadataExtract,
    ProcessedEntry,
    RawJSONEntry,
    SystemMessageEntry,
    UserMessageEntry,
)
from claude_monitor.utils.time_utils import TimezoneHandler

FIELD_COST_USD = "cost_usd"
FIELD_MODEL = "model"
TOKEN_INPUT = "input_tokens"
TOKEN_OUTPUT = "output_tokens"

logger = logging.getLogger(__name__)


def _parse_claude_entry(
    raw_data: RawJSONEntry,
) -> ClaudeMessageEntry | None:
    """Parse raw JSON dict into specific ClaudeJSONEntry type by inferring from structure.

    Real Claude Code JSONL files don't have explicit 'type' fields, so we infer:
    - Assistant entries: have 'usage' or token fields and 'model'
    - User entries: have 'message' with content but no usage/model
    - System entries: have 'content' field directly

    Args:
        raw_data: Raw dictionary from JSON.loads()

    Returns:
        Specific ClaudeJSONEntry type or None if invalid
    """
    from typing import cast

    # Check for explicit type field first (for future compatibility)
    explicit_type = raw_data.get("type")
    if explicit_type in ("system", "user", "assistant"):
        if explicit_type == "system":
            return cast(SystemMessageEntry, raw_data)
        elif explicit_type == "user":
            return cast(UserMessageEntry, raw_data)
        elif explicit_type == "assistant":
            return cast(AssistantMessageEntry, raw_data)

    # Infer type from data structure (for real Claude Code data)

    # Assistant entries: have usage/token data and model
    if (
        raw_data.get("model")
        or raw_data.get("usage")
        or any(
            key in raw_data
            for key in [
                "input_tokens",
                "output_tokens",
                "cache_creation_tokens",
                "cache_read_tokens",
            ]
        )
    ):
        return cast(AssistantMessageEntry, raw_data)

    # System entries: have direct 'content' field
    if "content" in raw_data and isinstance(raw_data.get("content"), str):
        return cast(SystemMessageEntry, raw_data)

    # User entries: have 'message' field (but no usage data)
    if "message" in raw_data and isinstance(raw_data.get("message"), dict):
        return cast(UserMessageEntry, raw_data)

    # If we can't determine the type, treat as assistant (for backward compatibility)
    # Most Claude Code entries are assistant responses with token usage
    logger.debug(
        f"Could not determine entry type, treating as assistant: {list(raw_data.keys())}"
    )
    return cast(AssistantMessageEntry, raw_data)


def load_usage_entries(
    data_path: str | None = None,
    hours_back: int | None = None,
    mode: CostMode = CostMode.AUTO,
    include_raw: bool = False,
) -> tuple[list[UsageEntry], list[ClaudeMessageEntry] | None]:
    """Load and convert JSONL files to UsageEntry objects.

    Args:
        data_path: Path to Claude data directory (defaults to ~/.claude/projects)
        hours_back: Only include entries from last N hours
        mode: Cost calculation mode
        include_raw: Whether to return raw JSON data alongside entries

    Returns:
        Tuple of (usage_entries, raw_data) where raw_data is None unless include_raw=True
    """
    data_path_resolved = Path(
        data_path if data_path else "~/.claude/projects"
    ).expanduser()
    timezone_handler = TimezoneHandler()
    pricing_calculator = PricingCalculator()

    cutoff_time = None
    if hours_back:
        cutoff_time = datetime.now(tz.utc) - timedelta(hours=hours_back)

    jsonl_files = _find_jsonl_files(data_path_resolved)
    if not jsonl_files:
        logger.warning("No JSONL files found in %s", data_path_resolved)
        return [], None

    all_entries = list[UsageEntry]()
    raw_entries: list[ClaudeMessageEntry] | None = (
        list[ClaudeMessageEntry]() if include_raw else None
    )
    processed_hashes = set[str]()

    for file_path in jsonl_files:
        entries, raw_data = _process_single_file(
            file_path,
            mode,
            cutoff_time,
            processed_hashes,
            include_raw,
            timezone_handler,
            pricing_calculator,
        )
        all_entries.extend(entries)
        if include_raw and raw_data and raw_entries is not None:
            raw_entries.extend(raw_data)

    all_entries.sort(key=lambda e: e.timestamp)

    logger.info(
        f"Processed {len(all_entries)} entries from {len(jsonl_files)} files"
    )

    return all_entries, raw_entries


def load_all_raw_entries(
    data_path: str | None = None,
) -> list[ClaudeMessageEntry]:
    """Load all raw JSONL entries without processing.

    Args:
        data_path: Path to Claude data directory

    Returns:
        List of raw JSON dictionaries
    """
    data_path_resolved = Path(
        data_path if data_path else "~/.claude/projects"
    ).expanduser()
    jsonl_files = _find_jsonl_files(data_path_resolved)

    all_raw_entries = list[ClaudeMessageEntry]()
    for file_path in jsonl_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw_data = json.loads(line)
                        parsed_entry = _parse_claude_entry(raw_data)
                        if parsed_entry:
                            all_raw_entries.append(parsed_entry)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.exception(f"Error loading raw entries from {file_path}: {e}")

    return all_raw_entries


def _find_jsonl_files(data_path: Path) -> list[Path]:
    """Find all .jsonl files in the data directory."""
    if not data_path.exists():
        logger.warning("Data path does not exist: %s", data_path)
        return []
    return list(data_path.rglob("*.jsonl"))


def _process_single_file(
    file_path: Path,
    mode: CostMode,
    cutoff_time: datetime | None,
    processed_hashes: set[str],
    include_raw: bool,
    timezone_handler: TimezoneHandler,
    pricing_calculator: PricingCalculator,
) -> tuple[list[UsageEntry], list[ClaudeMessageEntry] | None]:
    """Process a single JSONL file."""
    entries = list[UsageEntry]()
    raw_data: list[ClaudeMessageEntry] | None = (
        list[ClaudeMessageEntry]() if include_raw else None
    )

    try:
        entries_read = 0
        entries_filtered = 0
        entries_mapped = 0

        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    entries_read += 1

                    if not _should_process_entry(
                        data, cutoff_time, processed_hashes, timezone_handler
                    ):
                        entries_filtered += 1
                        continue

                    entry = _map_to_usage_entry(
                        data, mode, timezone_handler, pricing_calculator
                    )
                    if entry:
                        entries_mapped += 1
                        entries.append(entry)
                        _update_processed_hashes(data, processed_hashes)

                    if include_raw and raw_data is not None:
                        # Parse raw data to ClaudeJSONEntry for consistency
                        parsed_entry = _parse_claude_entry(data)
                        if parsed_entry:
                            raw_data.append(parsed_entry)

                except json.JSONDecodeError as e:
                    logger.debug(
                        f"Failed to parse JSON line in {file_path}: {e}"
                    )
                    continue

        logger.debug(
            f"File {file_path.name}: {entries_read} read, "
            f"{entries_filtered} filtered out, {entries_mapped} successfully mapped"
        )

    except Exception as e:
        logger.warning("Failed to read file %s: %s", file_path, e)
        report_file_error(
            exception=e,
            file_path=str(file_path),
            operation="read",
            additional_context={"file_exists": file_path.exists()},
        )
        return [], None

    return entries, raw_data


def _should_process_entry(
    data: RawJSONEntry,
    cutoff_time: datetime | None,
    processed_hashes: set[str],
    timezone_handler: TimezoneHandler,
) -> bool:
    """Check if entry should be processed based on time and uniqueness."""
    if cutoff_time:
        timestamp_str = data.get("timestamp")
        if timestamp_str:
            processor = TimestampProcessor(timezone_handler)
            timestamp = processor.parse_timestamp(timestamp_str)
            if timestamp and timestamp < cutoff_time:
                return False

    unique_hash = _create_unique_hash(data)
    return not (unique_hash and unique_hash in processed_hashes)


def _create_unique_hash(data: RawJSONEntry) -> str | None:
    """Create unique hash for deduplication."""
    # Extract message_id with type checking
    message_id = data.get("message_id")
    if not isinstance(message_id, str):
        message = data.get("message")
        if isinstance(message, dict):
            msg_id = message.get("id")
            message_id = msg_id if isinstance(msg_id, str) else None
        else:
            message_id = None

    # Extract request_id with type checking
    request_id = data.get("requestId") or data.get("request_id")
    if not isinstance(request_id, str):
        request_id = None

    return f"{message_id}:{request_id}" if message_id and request_id else None


def _update_processed_hashes(
    data: RawJSONEntry, processed_hashes: set[str]
) -> None:
    """Update the processed hashes set with current entry's hash."""
    unique_hash = _create_unique_hash(data)
    if unique_hash:
        processed_hashes.add(unique_hash)


def _map_to_usage_entry(
    raw_data: RawJSONEntry,
    mode: CostMode,
    timezone_handler: TimezoneHandler,
    pricing_calculator: PricingCalculator,
) -> UsageEntry | None:
    """Map raw data to UsageEntry with proper cost calculation."""
    try:
        # Parse raw data into specific ClaudeJSONEntry type
        claude_entry = _parse_claude_entry(raw_data)
        if not claude_entry:
            return None

        # _parse_claude_entry now infers types and only returns AssistantEntry for entries with token usage

        timestamp_processor = TimestampProcessor(timezone_handler)
        timestamp = timestamp_processor.parse_timestamp(
            claude_entry.get("timestamp", "")
        )
        if not timestamp:
            return None

        token_data = TokenExtractor.extract_tokens(claude_entry)
        if not any(v for k, v in token_data.items() if k != "total_tokens"):
            return None

        model = DataConverter.extract_model_name(
            claude_entry, default="unknown"
        )

        entry_data: ProcessedEntry = {
            FIELD_MODEL: model,
            TOKEN_INPUT: token_data["input_tokens"],
            TOKEN_OUTPUT: token_data["output_tokens"],
            "cache_creation_tokens": token_data.get("cache_creation_tokens", 0),
            "cache_read_tokens": token_data.get("cache_read_tokens", 0),
            FIELD_COST_USD: claude_entry.get("cost")
            or claude_entry.get(FIELD_COST_USD),
        }
        cost_usd = pricing_calculator.calculate_cost_for_entry(entry_data, mode)

        message = claude_entry.get("message", {})

        # Extract message_id with proper type handling
        msg_id_raw = claude_entry.get("message_id")
        msg_id_from_message = message.get("id") if message else ""
        message_id = (
            (msg_id_raw if isinstance(msg_id_raw, str) else "")
            or (
                msg_id_from_message
                if isinstance(msg_id_from_message, str)
                else ""
            )
            or ""
        )

        # Extract request_id with proper type handling
        req_id_raw = claude_entry.get("request_id") or claude_entry.get(
            "requestId"
        )
        request_id = req_id_raw if isinstance(req_id_raw, str) else "unknown"

        return UsageEntry(
            timestamp=timestamp,
            input_tokens=token_data["input_tokens"],
            output_tokens=token_data["output_tokens"],
            cache_creation_tokens=token_data.get("cache_creation_tokens", 0),
            cache_read_tokens=token_data.get("cache_read_tokens", 0),
            cost_usd=cost_usd,
            model=model,
            message_id=message_id,
            request_id=request_id,
        )

    except (KeyError, ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Failed to map entry: {type(e).__name__}: {e}")
        return None


class UsageEntryMapper:
    """Compatibility wrapper for legacy UsageEntryMapper interface.

    This class provides backward compatibility for tests that expect
    the old UsageEntryMapper interface, wrapping the new functional
    approach in _map_to_usage_entry.
    """

    def __init__(
        self,
        pricing_calculator: PricingCalculator,
        timezone_handler: TimezoneHandler,
    ):
        """Initialize with required components."""
        self.pricing_calculator = pricing_calculator
        self.timezone_handler = timezone_handler

    def map(self, data: RawJSONEntry, mode: CostMode) -> UsageEntry | None:
        """Map raw data to UsageEntry - compatibility interface."""
        return _map_to_usage_entry(
            data, mode, self.timezone_handler, self.pricing_calculator
        )

    def _has_valid_tokens(self, tokens: dict[str, int]) -> bool:
        """Check if tokens are valid (for test compatibility)."""
        return any(v > 0 for v in tokens.values())

    def _extract_timestamp(self, data: RawJSONEntry) -> datetime | None:
        """Extract timestamp (for test compatibility)."""
        timestamp = data.get("timestamp")
        if not timestamp:
            return None
        processor = TimestampProcessor(self.timezone_handler)
        return processor.parse_timestamp(timestamp)

    def _extract_model(self, data: RawJSONEntry) -> str:
        """Extract model name (for test compatibility)."""
        # Convert to ClaudeJSONEntry for compatibility
        parsed_data = _parse_claude_entry(data)
        if parsed_data:
            return DataConverter.extract_model_name(
                parsed_data, default="unknown"
            )
        return "unknown"

    def _extract_metadata(self, data: RawJSONEntry) -> MetadataExtract:
        """Extract metadata (for test compatibility)."""
        message = data.get("message", {})

        # Extract message_id with type checking
        message_id = data.get("message_id")
        if not isinstance(message_id, str):
            if message:
                msg_id = message.get("id", "")
                message_id = msg_id if isinstance(msg_id, str) else ""
            else:
                message_id = ""

        # Extract request_id with type checking
        request_id = data.get("request_id") or data.get("requestId")
        if not isinstance(request_id, str):
            request_id = "unknown"

        return {
            "message_id": message_id,
            "request_id": request_id,
        }
