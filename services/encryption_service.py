"""
`EncryptionService` — orchestrates a complete file-encryption operation.

Combines key derivation (`core.crypto`), output-path suggestion and
validation (`core.validators`), and streaming container writing
(`core.files`) into a single, cohesive service call. Workers
(`workers.crypto_worker`) invoke this; the UI never calls `core`
directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from core.crypto.key_derivation import derive_key
from core.files.container_writer import encrypt_file_to_container
from core.files.file_info import get_file_info, suggest_encrypted_output_path
from core.security.secure_memory import SecureBytes
from core.security.secure_random import generate_salt
from core.validators.file_validator import validate_input_file, validate_output_path
from core.validators.password_validator import validate_password
from services.settings_service import SettingsService
from utils.logger import get_logger

logger = get_logger()

ProgressCallback = Callable[[int, int], None]
CancelCheck = Callable[[], bool]


@dataclass(frozen=True, slots=True)
class EncryptionResult:
    """Returned by `EncryptionService.encrypt` on success."""

    source_path: Path
    output_path: Path
    original_size_bytes: int
    encrypted_size_bytes: int
    elapsed_seconds: float


class EncryptionService:
    """Stateless service coordinating a full file-encryption pipeline."""

    def encrypt(
        self,
        source_path: str | Path,
        password: str,
        *,
        output_path: str | Path | None = None,
        allow_overwrite: bool = False,
        progress_callback: ProgressCallback | None = None,
        cancel_check: CancelCheck | None = None,
    ) -> EncryptionResult:
        """
        Encrypt `source_path` with `password`.

        Args:
            source_path: File to encrypt. Validated before any work starts.
            password: Encryption password. Validated for minimum strength.
            output_path: Destination for the `.lockit` container. If None,
                defaults to `source_path + '.lockit'` in the same directory.
            allow_overwrite: If False (default) and `output_path` exists,
                raises `ValidationError` so the UI can ask for confirmation.
            progress_callback: `(bytes_done, total_bytes)` called from the
                calling thread — workers wrap this in a Qt signal emit.
            cancel_check: Returns True when the user has requested cancellation.

        Returns:
            `EncryptionResult` with paths, sizes, and elapsed time.

        Raises:
            ValidationError: Bad input file, bad password, or overwrite denied.
            OperationCancelledError: User cancelled.
            OSError: Disk-level failure.
        """
        import time

        # --- Validate inputs ---
        src = validate_input_file(source_path)
        validate_password(password)

        # Resolve output path: respect custom output directory from settings.
        ss = SettingsService.instance()
        active_settings = ss.settings
        if output_path is None:
            suggested = suggest_encrypted_output_path(src)
            if (
                active_settings.use_custom_output_directory
                and active_settings.custom_output_directory
            ):
                out_dir = Path(active_settings.custom_output_directory)
                suggested = out_dir / suggested.name
            output_path = suggested

        dest = Path(output_path) if output_path else suggest_encrypted_output_path(src)
        dest = validate_output_path(dest, allow_overwrite=allow_overwrite)

        source_info = get_file_info(src)
        # Use the live iteration count from settings for new encryptions.
        live_iterations = active_settings.pbkdf2_iterations
        logger.info(
            f"Encrypting '{src.name}' ({source_info.size_display}) → '{dest.name}' "
            f"[{live_iterations:,} PBKDF2 iterations]"
        )

        # --- Key derivation ---
        salt = generate_salt()
        started = time.monotonic()

        with SecureBytes(derive_key(password, salt, live_iterations)) as secure_key:
            encrypt_file_to_container(
                src,
                dest,
                key=secure_key.data,
                salt=salt,
                iterations=live_iterations,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )

        elapsed = time.monotonic() - started
        encrypted_size = dest.stat().st_size
        logger.info(
            f"Encrypted '{src.name}' in {elapsed:.2f}s "
            f"({source_info.size_bytes} → {encrypted_size} bytes)"
        )

        return EncryptionResult(
            source_path=src,
            output_path=dest,
            original_size_bytes=source_info.size_bytes,
            encrypted_size_bytes=encrypted_size,
            elapsed_seconds=elapsed,
        )
