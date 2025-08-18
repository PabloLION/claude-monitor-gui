"""Backport utilities for optional dependencies and compatibility.

This module isolates all type: ignore comments for optional imports
to maintain clean type checking in the main codebase.
"""

import sys


# TOML library backport
tomllib = None
try:
    # Python 3.11+
    import tomllib
except ImportError:
    try:
        # Python < 3.11 fallback
        import tomli as tomllib  # type: ignore[import-not-found]
    except ImportError:
        pass  # tomllib remains None


# Babel library backport
HAS_BABEL = False
try:
    from babel.dates import get_timezone_location  # type: ignore[import-not-found]

    HAS_BABEL = True  # type: ignore[assignment]
except ImportError:

    def get_timezone_location(
        timezone_name: str, locale_name: str = "en_US"
    ) -> str | None:
        """Fallback implementation when babel is not available."""
        del locale_name  # Mark as intentionally unused
        # Simple fallback - return None to indicate unavailable
        return None


# Platform-specific imports for terminal handling
HAS_TERMINAL_CONTROL = False
try:
    import select  # type: ignore[import-not-found]
    import termios  # type: ignore[import-not-found]
    import tty  # type: ignore[import-not-found]

    HAS_TERMINAL_CONTROL = True  # type: ignore[assignment]
except ImportError:
    # Windows or other platforms without these modules
    termios = None  # type: ignore[assignment]
    tty = None  # type: ignore[assignment]
    select = None  # type: ignore[assignment]


# Windows-specific imports
if sys.platform == "win32":
    try:
        import winreg  # type: ignore[import-not-found]

        HAS_WINREG = True
    except ImportError:
        winreg = None  # type: ignore[assignment]
        HAS_WINREG = False
else:
    winreg = None  # type: ignore[assignment]
    HAS_WINREG = False


__all__ = [
    "tomllib",
    "get_timezone_location",
    "HAS_BABEL",
    "termios",
    "tty",
    "select",
    "HAS_TERMINAL_CONTROL",
    "winreg",
    "HAS_WINREG",
]
