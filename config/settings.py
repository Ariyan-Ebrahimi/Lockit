"""
User-persisted application settings for LockIt.

Uses Pydantic for validation and JSON for serialisation so the settings
file is human-readable and easy to reset by deleting it. All values have
safe defaults — if the file is missing or corrupt, LockIt silently
starts with the defaults rather than crashing.

Settings are loaded once at startup via `SettingsService` (services/)
and written on every change. The model is designed for forward
compatibility: unknown keys are ignored on load so a settings file from
a future version of LockIt can be opened by an older version.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from core.crypto.constants import PBKDF2_DEFAULT_ITERATIONS

# PBKDF2 iteration-count bounds exposed in the Settings UI.
# These are not cryptographic limits — they are UX limits for the slider.
ITERATIONS_MIN: int = 100_000
ITERATIONS_MAX: int = 1_000_000
ITERATIONS_STEP: int = 50_000


class AppSettings(BaseModel):
    """
    Complete set of user-configurable preferences.

    Every field has a default so that a missing or partially-written
    file still produces a valid, safe configuration.
    """

    model_config = {"extra": "ignore"}  # Forward-compat: unknown keys are silently dropped.

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------
    pbkdf2_iterations: int = Field(
        default=PBKDF2_DEFAULT_ITERATIONS,
        description=(
            "PBKDF2-HMAC-SHA256 iteration count used when encrypting new files. "
            "Higher values are slower but more resistant to brute-force attacks. "
            "Stored per-file in the container header, so changing this does not "
            "affect previously encrypted files."
        ),
    )

    # ------------------------------------------------------------------
    # File output
    # ------------------------------------------------------------------
    use_custom_output_directory: bool = Field(
        default=False,
        description=(
            "When True, encrypted/decrypted files are written to "
            "`custom_output_directory`. When False, output goes alongside the "
            "source file."
        ),
    )
    custom_output_directory: str = Field(
        default="",
        description="Absolute path to the preferred output directory.",
    )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    log_level: str = Field(
        default="INFO",
        description="Minimum log level written to the log file. DEBUG | INFO | WARNING | ERROR",
    )

    # ------------------------------------------------------------------
    # UI state (persisted for convenience; not user-editable in the UI)
    # ------------------------------------------------------------------
    sidebar_collapsed: bool = Field(
        default=False,
        description="Whether the sidebar was collapsed when the app last closed.",
    )

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("pbkdf2_iterations")
    @classmethod
    def clamp_iterations(cls, v: int) -> int:
        return max(ITERATIONS_MIN, min(ITERATIONS_MAX, v))

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR"}
        upper = v.upper()
        return upper if upper in allowed else "INFO"

    @field_validator("custom_output_directory")
    @classmethod
    def normalise_directory(cls, v: str) -> str:
        return v.strip()
