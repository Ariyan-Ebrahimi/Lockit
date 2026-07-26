"""
Streaming `.lockit` container writer.

Encrypts a source file to a `.lockit` container in fixed-size chunks so
that arbitrarily large files can be encrypted using constant memory,
with progress reported after every chunk.
"""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Callable

from core.crypto.cipher_engine import AesGcmCipherEngine
from core.crypto.constants import PBKDF2_DEFAULT_ITERATIONS, STREAM_CHUNK_SIZE_BYTES
from core.files.container_format import (
    build_chunk_associated_data,
    pack_chunk_prefix,
    pack_header,
)
from core.files.exceptions import OperationCancelledError
from core.security.secure_random import generate_nonce

ProgressCallback = Callable[[int, int], None]
CancelCheck = Callable[[], bool]


def encrypt_file_to_container(
    source_path: str | Path,
    destination_path: str | Path,
    *,
    key: bytes,
    salt: bytes,
    iterations: int = PBKDF2_DEFAULT_ITERATIONS,
    chunk_size: int = STREAM_CHUNK_SIZE_BYTES,
    progress_callback: ProgressCallback | None = None,
    cancel_check: CancelCheck | None = None,
) -> None:
    """
    Encrypt `source_path` into a `.lockit` container at `destination_path`.

    Args:
        source_path: The plaintext file to encrypt.
        destination_path: Where to write the `.lockit` container. Any
            existing file here is overwritten — callers must run
            `core.validators.file_validator.validate_output_path` first
            to enforce the "never overwrite without confirmation" policy.
        key: A 32-byte AES-256 key (from `core.crypto.derive_key`).
            Callers are responsible for wiping it afterward, e.g. via
            `core.security.SecureBytes`.
        salt: The PBKDF2 salt used to derive `key`, stored in the
            container header so the same key can be re-derived later
            from the user's password.
        iterations: The PBKDF2 iteration count used to derive `key`,
            stored in the header for the same reason.
        chunk_size: Plaintext bytes read and encrypted per chunk.
        progress_callback: Called after every chunk with
            `(bytes_processed, total_bytes)`.
        cancel_check: Called before every chunk; if it returns True,
            the operation stops and `OperationCancelledError` is raised.
            The partially-written destination file is deleted first.

    Raises:
        OperationCancelledError: If `cancel_check` signaled cancellation.
        OSError: For underlying file I/O failures (disk full, permissions).
    """
    source = Path(source_path)
    destination = Path(destination_path)
    total_bytes = source.stat().st_size

    try:
        with source.open("rb") as source_file, destination.open("wb") as dest_file:
            dest_file.write(pack_header(iterations=iterations, salt=salt))
            _write_chunks(
                source_file,
                dest_file,
                key=key,
                total_bytes=total_bytes,
                chunk_size=chunk_size,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )
    except OperationCancelledError:
        destination.unlink(missing_ok=True)
        raise
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def _write_chunks(
    source_file: BinaryIO,
    dest_file: BinaryIO,
    *,
    key: bytes,
    total_bytes: int,
    chunk_size: int,
    progress_callback: ProgressCallback | None,
    cancel_check: CancelCheck | None,
) -> None:
    bytes_processed = 0
    chunk_index = 0

    # A zero-byte source still needs exactly one (empty, is_last=True)
    # chunk written so the reader has a definitive end-of-stream marker.
    while True:
        if cancel_check is not None and cancel_check():
            raise OperationCancelledError()

        plaintext_chunk = source_file.read(chunk_size)
        is_last = (
            len(plaintext_chunk) < chunk_size
            or bytes_processed + len(plaintext_chunk) >= total_bytes
        )

        nonce = generate_nonce()
        associated_data = build_chunk_associated_data(chunk_index=chunk_index, is_last=is_last)
        ciphertext = AesGcmCipherEngine.encrypt(plaintext_chunk, key, nonce, associated_data)

        dest_file.write(
            pack_chunk_prefix(nonce=nonce, is_last=is_last, ciphertext_length=len(ciphertext))
        )
        dest_file.write(ciphertext)

        bytes_processed += len(plaintext_chunk)
        chunk_index += 1

        if progress_callback is not None:
            progress_callback(min(bytes_processed, total_bytes), total_bytes)

        if is_last:
            break
