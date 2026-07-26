"""Exceptions specific to file-level encrypt/decrypt operations."""

from __future__ import annotations


class OperationCancelledError(Exception):
    """
    Raised when an in-progress encrypt/decrypt operation is cancelled by
    the user (via the `cancel_check` callback passed to the writer/reader).

    Callers (the Phase 5 worker threads) catch this to clean up any
    partially-written output file rather than treating it as a failure.
    """
