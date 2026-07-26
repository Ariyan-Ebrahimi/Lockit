"""
Centralized logging configuration for LockIt.

Uses loguru for structured, rotating, thread-safe logging. Security note:
this module must never log secrets, passwords, derived keys, or raw file
contents. Callers are responsible for keeping log messages free of
sensitive data; see `core/security` (Phase 3) for guidance on what is
safe to log.
"""

from __future__ import annotations

import sys

from loguru import logger

from config.constants import LOG_RETENTION_COUNT, LOG_ROTATION_SIZE
from config.paths import get_log_file_path

_configured = False


def configure_logging(*, verbose: bool = False) -> None:
    """
    Configure the global loguru logger with a console sink and a rotating
    file sink. Safe to call multiple times; only configures once.

    Args:
        verbose: When True, emit DEBUG-level logs to the console.
                 Otherwise, console logging is limited to INFO and above.
    """
    global _configured
    if _configured:
        return

    logger.remove()  # Remove the default handler to control formatting.

    # PyInstaller GUI builds (console=False / --windowed) may set
    # sys.stderr to None. Only attach a console sink when a real stream
    # is available; the rotating file sink below is always enabled.
    if sys.stderr is not None:
        console_level = "DEBUG" if verbose else "INFO"
        logger.add(
            sys.stderr,
            level=console_level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
                "- <level>{message}</level>"
            ),
            colorize=True,
            backtrace=False,
            diagnose=False,
        )

    logger.add(
        get_log_file_path(),
        level="DEBUG",
        rotation=LOG_ROTATION_SIZE,
        retention=LOG_RETENTION_COUNT,
        compression="zip",
        encoding="utf-8",
        backtrace=False,
        diagnose=False,
        enqueue=True,  # Thread-safe writes from background workers.
    )

    _configured = True
    logger.debug("Logging initialized.")


def get_logger():
    """Return the configured loguru logger instance."""
    return logger
