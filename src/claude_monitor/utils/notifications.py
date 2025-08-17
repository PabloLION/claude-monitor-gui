"""Notification management utilities."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from claude_monitor.types import JSONSerializable


class NotificationManager:
    """Manages notification states and persistence."""

    def __init__(self, config_dir: Path) -> None:
        self.notification_file: Path = config_dir / "notification_states.json"
        self.states: dict[str, dict[str, bool | datetime | None]] = (
            self._load_states()
        )

        self.default_states: dict[str, dict[str, bool | datetime | None]] = {
            "switch_to_custom": {"triggered": False, "timestamp": None},
            "exceed_max_limit": {"triggered": False, "timestamp": None},
            "tokens_will_run_out": {"triggered": False, "timestamp": None},
        }

    def _load_states(self) -> dict[str, dict[str, bool | datetime | None]]:
        """Load notification states from file."""
        if not self.notification_file.exists():
            return {
                "switch_to_custom": {"triggered": False, "timestamp": None},
                "exceed_max_limit": {"triggered": False, "timestamp": None},
                "tokens_will_run_out": {"triggered": False, "timestamp": None},
            }

        try:
            with open(self.notification_file) as f:
                states: dict[str, dict[str, JSONSerializable]] = json.load(f)
                # Convert timestamp strings back to datetime objects
                parsed_states: dict[
                    str, dict[str, bool | datetime | None]
                ] = {}
                for key, state in states.items():
                    parsed_state: dict[str, bool | datetime | None] = {
                        "triggered": bool(state.get("triggered", False)),
                        "timestamp": None,
                    }
                    timestamp_value = state.get("timestamp")
                    if timestamp_value and isinstance(timestamp_value, str):
                        parsed_state["timestamp"] = datetime.fromisoformat(
                            timestamp_value
                        )
                    parsed_states[key] = parsed_state
                return parsed_states
        except (json.JSONDecodeError, FileNotFoundError, ValueError):
            return self.default_states.copy()

    def _save_states(self) -> None:
        """Save notification states to file."""
        try:
            states_to_save: dict[str, dict[str, bool | str | None]] = {}
            for key, state in self.states.items():
                timestamp_str: str | None = None
                timestamp_value = state["timestamp"]
                if isinstance(timestamp_value, datetime):
                    timestamp_str = timestamp_value.isoformat()

                states_to_save[key] = {
                    "triggered": bool(state["triggered"]),
                    "timestamp": timestamp_str,
                }

            with open(self.notification_file, "w") as f:
                json.dump(states_to_save, f, indent=2)
        except (OSError, TypeError, ValueError) as e:
            import logging

            logging.getLogger(__name__).warning(
                f"Failed to save notification states to {self.notification_file}: {e}"
            )

    def should_notify(self, key: str, cooldown_hours: int | float = 24) -> bool:
        """Check if notification should be shown."""
        if key not in self.states:
            self.states[key] = {"triggered": False, "timestamp": None}
            return True

        state = self.states[key]
        if not state["triggered"]:
            return True

        timestamp_value = state["timestamp"]
        if timestamp_value is None:
            return True

        if not isinstance(timestamp_value, datetime):
            return True

        now: datetime = datetime.now()
        time_since_last: timedelta = now - timestamp_value
        cooldown_seconds: float = cooldown_hours * 3600
        return time_since_last.total_seconds() >= cooldown_seconds

    def mark_notified(self, key: str) -> None:
        """Mark notification as shown."""
        now: datetime = datetime.now()
        self.states[key] = {"triggered": True, "timestamp": now}
        self._save_states()

    def get_notification_state(
        self, key: str
    ) -> dict[str, bool | datetime | None]:
        """Get current notification state."""
        default_state: dict[str, bool | datetime | None] = {
            "triggered": False,
            "timestamp": None,
        }
        return self.states.get(key, default_state)

    def is_notification_active(self, key: str) -> bool:
        """Check if notification is currently active."""
        state = self.get_notification_state(key)
        triggered_value = state["triggered"]
        timestamp_value = state["timestamp"]
        return bool(triggered_value) and timestamp_value is not None
