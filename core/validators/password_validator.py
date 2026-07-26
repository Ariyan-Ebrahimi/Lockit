"""
Password validation rules for LockIt.

Enforces the minimum bar a password must clear before it is used to
derive an encryption key. This runs *before* any cryptographic work
begins, so the UI (Phase 5/6) can reject a weak password immediately
with a clear message rather than silently producing a weakly-protected
file.
"""

from __future__ import annotations

from core.security.password_strength import PasswordStrengthResult, score_password
from core.validators.exceptions import ValidationError

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 512  # Defends against pathological input; PBKDF2 has no real upper bound.


def validate_password(password: str, *, require_acceptable_strength: bool = True) -> None:
    """
    Validate a password meets LockIt's minimum requirements.

    Args:
        password: The candidate password.
        require_acceptable_strength: When True (the default), also
            rejects passwords scoring below `PasswordStrength.FAIR`.
            Callers that only need the hard length/emptiness checks
            (e.g. the decrypt flow, where any password the user set is
            valid) can pass False.

    Raises:
        ValidationError: If the password is empty, too short, too long,
            or (when `require_acceptable_strength`) too weak.
    """
    if not password:
        raise ValidationError("Password cannot be empty.")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")

    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValidationError(f"Password must be at most {MAX_PASSWORD_LENGTH} characters.")

    if require_acceptable_strength:
        result: PasswordStrengthResult = score_password(password)
        if not result.is_acceptable:
            reason = " ".join(result.feedback) if result.feedback else "Password is too weak."
            raise ValidationError(f"Password is too weak. {reason}")


def passwords_match(password: str, confirmation: str) -> bool:
    """Check that a password and its confirmation entry are identical."""
    return password == confirmation
