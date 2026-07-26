"""
`DecryptionService` — orchestrates a complete file-decryption operation.

Reads the container header (to recover the stored salt and KDF
iteration count), re-derives the key from the user's password, and
streams the plaintext back to disk.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from core.crypto.key_derivation import derive_key
from core.files.container_reader import decrypt_container_to_file, read_container_header
from core.files.file_info import get_file_info, suggest_decrypted_output_path
from core.security.secure_memory import SecureBytes
from core.validators.file_validator import validate_input_file, validate_output_path
from core.validators.password_validator import validate_password
from services.settings_service import SettingsService
from utils.logger import get_logger

logger = get_logger()

ProgressCallback = Callable[[int, int], None]
CancelCheck = Callable[[], bool]


@dataclass(frozen=True, slots=True)
class DecryptionResult:
    """Returned by `DecryptionService.decrypt` on success."""

    source_path: Path
    output_path: Path
    decrypted_size_bytes: int
    elapsed_seconds: float


class DecryptionService:
    """Stateless service coordinating a full file-decryption pipeline."""

    def decrypt(
        self,
        source_path: str | Path,
        password: str,
        *,
        output_path: str | Path | None = None,
        allow_overwrite: bool = False,
        progress_callback: ProgressCallback | None = None,
        cancel_check: CancelCheck | None = None,
    ) -> DecryptionResult:
        """
        Decrypt a `.lockit` container at `source_path` with `password`.

        Args:
            source_path: The `.lockit` container to decrypt.
            password: The password originally used to encrypt the file.
                Not strength-validated here — any non-empty password is
                attempted (wrong password produces an auth failure from
                the crypto layer, not a validation error).
            output_path: Where to write the recovered plaintext. Defaults
                to the path suggested by `suggest_decrypted_output_path`.
            allow_overwrite: See `EncryptionService.encrypt`.
            progress_callback / cancel_check: Same semantics as encrypt.

        Returns:
            `DecryptionResult` with paths, sizes, and elapsed time.

        Raises:
            ValidationError: Bad input file path or empty password.
            UnsupportedFileFormatError: File is not a valid `.lockit` container.
            InvalidPasswordOrCorruptedDataError: Wrong password or corrupt data.
            TruncatedFileError: Container appears truncated.
            OperationCancelledError: User cancelled.
            OSError: Disk-level failure.
        """
        import time

        # --- Validate inputs ---
        src = validate_input_file(source_path)
        # Decrypt accepts any non-empty password — strength is irrelevant here.
        validate_password(password, require_acceptable_strength=False)

        # Resolve output path: respect custom output directory from settings.
        ss = SettingsService.instance()
        active_settings = ss.settings
        if output_path is None:
            suggested = suggest_decrypted_output_path(src)
            if (
                active_settings.use_custom_output_directory
                and active_settings.custom_output_directory
            ):
                out_dir = Path(active_settings.custom_output_directory)
                suggested = out_dir / suggested.name
            output_path = suggested

        dest = Path(output_path)
        dest = validate_output_path(dest, allow_overwrite=allow_overwrite)

        source_info = get_file_info(src)
        logger.info(f"Decrypting '{src.name}' ({source_info.size_display}) → '{dest.name}'")

        # --- Read header to get stored KDF parameters ---
        _version, iterations, salt = read_container_header(src)

        # --- Key derivation + decryption ---
        started = time.monotonic()

        with SecureBytes(derive_key(password, salt, iterations)) as secure_key:
            decrypt_container_to_file(
                src,
                dest,
                key=secure_key.data,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )

        elapsed = time.monotonic() - started
        decrypted_size = dest.stat().st_size
        logger.info(
            f"Decrypted '{src.name}' in {elapsed:.2f}s ({decrypted_size} bytes recovered)"
        )

        return DecryptionResult(
            source_path=src,
            output_path=dest,
            decrypted_size_bytes=decrypted_size,
            elapsed_seconds=elapsed,
        )
