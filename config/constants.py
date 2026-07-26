"""
Application-wide constants for LockIt.

This module centralizes immutable values used throughout the application:
metadata, sizing defaults, and encoding conventions. Cryptographic
parameter constants live in `core/crypto` (added in Phase 3) to keep
security-critical values close to the code that uses them.
"""

from __future__ import annotations

from typing import Final

# --------------------------------------------------------------------------
# Application metadata
# --------------------------------------------------------------------------
APP_NAME: Final[str] = "LockIt"
APP_DISPLAY_NAME: Final[str] = "LockIt — File Encryption"
APP_VERSION: Final[str] = "0.1.0"
APP_ORGANIZATION: Final[str] = "LockIt"
APP_ORGANIZATION_DOMAIN: Final[str] = "lockit.app"
APP_DESCRIPTION: Final[str] = "Secure, modern file encryption for everyone."

# --------------------------------------------------------------------------
# Window defaults
# --------------------------------------------------------------------------
DEFAULT_WINDOW_WIDTH: Final[int] = 1200
DEFAULT_WINDOW_HEIGHT: Final[int] = 800
MIN_WINDOW_WIDTH: Final[int] = 960
MIN_WINDOW_HEIGHT: Final[int] = 640

SIDEBAR_WIDTH_EXPANDED: Final[int] = 240
SIDEBAR_WIDTH_COLLAPSED: Final[int] = 72

# --------------------------------------------------------------------------
# Encoding / file conventions
# --------------------------------------------------------------------------
ENCRYPTED_FILE_EXTENSION: Final[str] = ".lockit"
TEXT_ENCODING: Final[str] = "utf-8"

# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------
LOG_FILE_NAME: Final[str] = "lockit.log"
LOG_ROTATION_SIZE: Final[str] = "5 MB"
LOG_RETENTION_COUNT: Final[int] = 5
