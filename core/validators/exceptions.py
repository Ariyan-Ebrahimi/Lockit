"""Shared exception type for LockIt's input validation layer."""

from __future__ import annotations


class ValidationError(Exception):
    """
    Raised when user-provided input (a password, a file path) fails a
    validation rule. Carries a message safe to display directly in the
    UI — never includes the invalid value itself when that value is
    sensitive (e.g. a password).
    """
