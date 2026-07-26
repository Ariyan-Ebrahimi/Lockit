"""Public API for LockIt's input validation layer."""

from __future__ import annotations

from core.validators.exceptions import ValidationError
from core.validators.file_validator import (
    MAX_RECOMMENDED_FILE_SIZE_BYTES,
    is_oversized,
    validate_input_file,
    validate_output_path,
)
from core.validators.password_validator import (
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    passwords_match,
    validate_password,
)

__all__ = [
    "ValidationError",
    "MAX_PASSWORD_LENGTH",
    "MIN_PASSWORD_LENGTH",
    "passwords_match",
    "validate_password",
    "MAX_RECOMMENDED_FILE_SIZE_BYTES",
    "is_oversized",
    "validate_input_file",
    "validate_output_path",
]
