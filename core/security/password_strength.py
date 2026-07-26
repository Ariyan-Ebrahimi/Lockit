"""
Password strength scoring for LockIt.

Provides a heuristic strength score used by the UI's password strength
indicator (wired up in Phase 6) and by `core.validators.password_validator`
to reject passwords too weak to meaningfully protect a file.

This is intentionally a local, dependency-free heuristic (length +
character-class diversity + common-pattern penalties) rather than a
call to an external API — password strength must never leave the
machine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import IntEnum

_MIN_RECOMMENDED_LENGTH = 12

_COMMON_SEQUENCES = (
    "0123456789",
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
    "password",
    "letmein",
    "admin",
)


class PasswordStrength(IntEnum):
    """Discrete strength tiers, ordered weakest to strongest."""

    VERY_WEAK = 0
    WEAK = 1
    FAIR = 2
    STRONG = 3
    VERY_STRONG = 4


@dataclass(frozen=True, slots=True)
class PasswordStrengthResult:
    """Result of scoring a password: a tier plus actionable feedback."""

    strength: PasswordStrength
    score: int  # 0-100, for smooth progress-bar rendering in the UI
    feedback: tuple[str, ...]

    @property
    def is_acceptable(self) -> bool:
        """Whether this password meets LockIt's minimum bar for encrypting files."""
        return self.strength >= PasswordStrength.FAIR


def _contains_common_sequence(lowered: str) -> bool:
    return any(seq in lowered for seq in _COMMON_SEQUENCES if len(seq) >= 4)


def _has_repeated_run(password: str, run_length: int = 4) -> bool:
    """Detect a character repeated `run_length` or more times in a row (e.g. 'aaaa')."""
    return re.search(r"(.)\1{" + str(run_length - 1) + r",}", password) is not None


def score_password(password: str) -> PasswordStrengthResult:
    """
    Score a password's strength using length and character-class diversity,
    with penalties for common weak patterns.

    Args:
        password: The candidate password (never logged or persisted).

    Returns:
        A `PasswordStrengthResult` with a discrete tier, a 0-100 score
        for UI progress bars, and human-readable feedback messages.
    """
    feedback: list[str] = []

    if not password:
        return PasswordStrengthResult(PasswordStrength.VERY_WEAK, 0, ("Password is empty.",))

    length = len(password)
    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_symbol = bool(re.search(r"[^a-zA-Z0-9]", password))
    class_count = sum([has_lower, has_upper, has_digit, has_symbol])

    # Weight raw length by character diversity (unique characters / total).
    # A long password made of one repeated character (e.g. "aaaaaaaaaaaa")
    # has near-zero entropy and must not score like a genuinely long,
    # varied password just because len() is large.
    unique_ratio = len(set(password)) / length
    effective_length = length * (0.4 + 0.6 * unique_ratio)

    # Base score from length, capped, then scaled by character diversity.
    length_score = min(effective_length / _MIN_RECOMMENDED_LENGTH, 1.5) * 55
    diversity_score = (class_count / 4) * 35
    score = length_score + diversity_score

    lowered = password.lower()
    if _contains_common_sequence(lowered):
        score -= 25
        feedback.append("Avoid common words or keyboard sequences.")

    if _has_repeated_run(password):
        score -= 25
        feedback.append("Avoid repeating the same character many times in a row.")

    if length < _MIN_RECOMMENDED_LENGTH:
        feedback.append(f"Use at least {_MIN_RECOMMENDED_LENGTH} characters.")

    if class_count < 3:
        feedback.append("Mix uppercase, lowercase, numbers, and symbols.")

    score = max(0, min(100, round(score)))

    if score >= 85:
        tier = PasswordStrength.VERY_STRONG
    elif score >= 65:
        tier = PasswordStrength.STRONG
    elif score >= 45:
        tier = PasswordStrength.FAIR
    elif score >= 20:
        tier = PasswordStrength.WEAK
    else:
        tier = PasswordStrength.VERY_WEAK

    if not feedback and tier >= PasswordStrength.STRONG:
        feedback.append("Strong password.")

    return PasswordStrengthResult(tier, score, tuple(feedback))
