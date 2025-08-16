"""Unified session monitoring - combines tracking and validation."""

import logging
from collections.abc import Callable

from claude_monitor.core.models import AnalysisResult

logger = logging.getLogger(__name__)


class SessionMonitor:
    """Monitors sessions with tracking and validation."""

    def __init__(self) -> None:
        """Initialize session monitor."""
        self._current_session_id: str | None = None
        self._session_callbacks: list[
            Callable[[str, str, dict[str, str | int | float] | None], None]
        ] = []
        self._session_history: list[dict[str, str | int | float]] = []

    def update(self, data: dict[str, list[dict[str, str | int | float | bool]] | int | str] | AnalysisResult) -> tuple[bool, list[str]]:
        """Update session tracking with new data and validate.

        Args:
            data: Monitoring data with blocks

        Returns:
            Tuple of (is_valid, error_messages)
        """
        is_valid: bool
        errors: list[str]
        is_valid, errors = self.validate_data(data)
        if not is_valid:
            logger.warning(f"Data validation failed: {errors}")
            return is_valid, errors

        blocks_raw = data.get("blocks", [])
        if not isinstance(blocks_raw, list):
            return False, ["blocks must be a list"]
        blocks: list[dict[str, str | int | float | bool]] = blocks_raw

        active_session: dict[str, str | int | float | bool] | None = None
        for block in blocks:
            if block.get("isActive", False):
                active_session = block
                break

        if active_session:
            session_id_raw = active_session.get("id")
            if isinstance(session_id_raw, str) and session_id_raw != self._current_session_id:
                self._on_session_change(
                    self._current_session_id, session_id_raw, active_session
                )
                self._current_session_id = session_id_raw
        elif self._current_session_id is not None:
            self._on_session_end(self._current_session_id)
            self._current_session_id = None

        return is_valid, errors

    def validate_data(self, data: dict[str, list[dict[str, str | int | float | bool]] | int | str]) -> tuple[bool, list[str]]:
        """Validate monitoring data structure and content.

        Args:
            data: Data to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors: list[str] = list[str]()

        if not isinstance(data, dict):
            errors.append("Data must be a dictionary")
            return False, errors

        if "blocks" not in data:
            errors.append("Missing required key: blocks")

        if "blocks" in data:
            blocks_raw = data["blocks"]
            if not isinstance(blocks_raw, list):
                errors.append("blocks must be a list")
            else:
                for i, block in enumerate(blocks_raw):
                    block_errors: list[str] = self._validate_block(block, i)
                    errors.extend(block_errors)

        return len(errors) == 0, errors

    def _validate_block(self, block: dict[str, str | int | float | bool], index: int) -> list[str]:
        """Validate individual block.

        Args:
            block: Block to validate
            index: Block index for error messages

        Returns:
            List of error messages
        """
        errors: list[str] = list[str]()

        if not isinstance(block, dict):
            errors.append(f"Block {index} must be a dictionary")
            return errors

        required_fields: list[str] = ["id", "isActive", "totalTokens", "costUSD"]
        for field in required_fields:
            if field not in block:
                errors.append(f"Block {index} missing required field: {field}")

        if "totalTokens" in block and not isinstance(
            block["totalTokens"], (int, float)
        ):
            errors.append(f"Block {index} totalTokens must be numeric")

        if "costUSD" in block and not isinstance(block["costUSD"], (int, float)):
            errors.append(f"Block {index} costUSD must be numeric")

        if "isActive" in block and not isinstance(block["isActive"], bool):
            errors.append(f"Block {index} isActive must be boolean")

        return errors

    def _on_session_change(
        self, old_id: str | None, new_id: str, session_data: dict[str, str | int | float]
    ) -> None:
        """Handle session change.

        Args:
            old_id: Previous session ID
            new_id: New session ID
            session_data: New session data
        """
        if old_id is None:
            logger.info(f"New session started: {new_id}")
        else:
            logger.info(f"Session changed from {old_id} to {new_id}")

        start_time = session_data.get("startTime")
        self._session_history.append(
            {
                "id": new_id,
                "started_at": start_time if start_time is not None else "",
                "tokens": session_data.get("totalTokens", 0),
                "cost": session_data.get("costUSD", 0),
            }
        )

        for callback in self._session_callbacks:
            try:
                callback("session_start", new_id, session_data)
            except Exception as e:
                logger.exception(f"Session callback error: {e}")

    def _on_session_end(self, session_id: str) -> None:
        """Handle session end.

        Args:
            session_id: Ended session ID
        """
        logger.info(f"Session ended: {session_id}")

        for callback in self._session_callbacks:
            try:
                callback("session_end", session_id, None)
            except Exception as e:
                logger.exception(f"Session callback error: {e}")

    def register_callback(
        self, callback: Callable[[str, str, dict[str, str | int | float] | None], None]
    ) -> None:
        """Register session change callback.

        Args:
            callback: Function(event_type, session_id, session_data)
        """
        if callback not in self._session_callbacks:
            self._session_callbacks.append(callback)

    def unregister_callback(
        self, callback: Callable[[str, str, dict[str, str | int | float] | None], None]
    ) -> None:
        """Unregister session change callback.

        Args:
            callback: Callback to remove
        """
        if callback in self._session_callbacks:
            self._session_callbacks.remove(callback)

    @property
    def current_session_id(self) -> str | None:
        """Get current active session ID."""
        return self._current_session_id

    @property
    def session_count(self) -> int:
        """Get total number of sessions tracked."""
        return len(self._session_history)

    @property
    def session_history(self) -> list[dict[str, str | int | float]]:
        """Get session history."""
        return self._session_history.copy()
