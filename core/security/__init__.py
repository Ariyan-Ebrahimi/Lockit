"""
Public API for LockIt's security utilities: secure memory handling,
secure randomness, and password strength scoring.
"""

from __future__ import annotations

from core.security.password_strength import (
    PasswordStrength,
    PasswordStrengthResult,
    score_password,
)
from core.security.secure_memory import SecureBytes, wipe_bytearray
from core.security.secure_random import (
    constant_time_compare,
    generate_nonce,
    generate_salt,
    generate_secure_token,
)

__all__ = [
    "PasswordStrength",
    "PasswordStrengthResult",
    "score_password",
    "SecureBytes",
    "wipe_bytearray",
    "constant_time_compare",
    "generate_nonce",
    "generate_salt",
    "generate_secure_token",
]
