"""Backport utilities for optional dependencies and compatibility.

This module isolates all type: ignore comments for optional imports
to maintain clean type checking in the main codebase.
"""

__all__ = [
    "tomllib",
    "HAS_TOMLLIB",
    "HAS_BABEL",
    "termios",
    "tty",
    "select",
    "HAS_TERMINAL_CONTROL",
    "winreg",
    "HAS_WINREG",
]
import sys


# TOML library backport
try:
    # Python 3.11+
    import tomllib

    HAS_TOMLLIB = True
except ImportError:
    try:
        # Python < 3.11 fallback
        import tomli as tomllib  # pyright: ignore[reportMissingImports]
    except ImportError:
        HAS_TOMLLIB = False  # pyright: ignore[reportConstantRedefinition]


# Babel library backport
HAS_BABEL = False
try:
    # fmt: off
    from babel.dates import ( # pyright: ignore[reportMissingImports]  # isort: skip
        get_timezone_location,  # pyright: ignore[reportUnknownVariableType]
    )
    # fmt: on

    HAS_BABEL = True  # pyright: ignore[reportConstantRedefinition]
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
    import select
    import termios
    import tty

    HAS_TERMINAL_CONTROL = True  # pyright: ignore[reportConstantRedefinition]
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
        winreg = None
        HAS_WINREG = False
else:
    winreg = None
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
