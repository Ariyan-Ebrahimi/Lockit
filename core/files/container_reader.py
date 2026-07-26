"""
Streaming `.lockit` container reader.

Decrypts a `.lockit` container back to its original plaintext file in
chunks, verifying authentication (and therefore both password
correctness and data integrity) on every chunk, with progress reported
throughout.
"""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Callable

from core.crypto.cipher_engine import AesGcmCipherEngine
from core.crypto.constants import CONTAINER_FORMAT_VERSION
from core.crypto.exceptions import TruncatedFileError, UnsupportedFileFormatError
from core.files.container_format import (
    CHUNK_PREFIX_SIZE_BYTES,
    HEADER_SIZE_BYTES,
    build_chunk_associated_data,
    unpack_chunk_prefix,
    unpack_header,
)
from core.files.exceptions import OperationCancelledError

ProgressCallback = Callable[[int, int], None]
CancelCheck = Callable[[], bool]


def read_container_header(path: str | Path) -> tuple[int, int, bytes]:
    """
    Read just the header of a `.lockit` container without decrypting
    any content — used to obtain the salt/iterations needed to derive
    the decryption key from the user's password before committing to a
    full decrypt pass.

    Returns:
        A tuple of (format_version, iterations, salt).

    Raises:
        UnsupportedFileFormatError: If the file isn't a valid/supported
            `.lockit` container.
    """
    file_path = Path(path)
    try:
        with file_path.open("rb") as f:
            header_bytes = f.read(HEADER_SIZE_BYTES)
            version, iterations, salt = unpack_header(header_bytes)
    except ValueError as exc:
        raise UnsupportedFileFormatError(str(exc)) from exc

    if version > CONTAINER_FORMAT_VERSION:
        raise UnsupportedFileFormatError(
            f"This file was created by a newer version of LockIt "
            f"(format v{version}) and cannot be opened by this version."
        )

    return version, iterations, salt


def decrypt_container_to_file(
    source_path: str | Path,
    destination_path: str | Path,
    *,
    key: bytes,
    progress_callback: ProgressCallback | None = None,
    cancel_check: CancelCheck | None = None,
) -> None:
    """
    Decrypt a `.lockit` container at `source_path` to `destination_path`.

    Args:
        source_path: The `.lockit` container to decrypt.
        destination_path: Where to write the recovered plaintext. Any
            existing file here is overwritten — callers must run
            `core.validators.file_validator.validate_output_path` first.
        key: The 32-byte AES-256 key derived from the user's password
            and the container's stored salt/iterations (see
            `read_container_header` + `core.crypto.derive_key`).
        progress_callback: Called after every chunk with
            `(bytes_processed, total_bytes)`.
        cancel_check: Called before every chunk; if it returns True,
            the operation stops and `OperationCancelledError` is raised.
            The partially-written destination file is deleted first.

    Raises:
        UnsupportedFileFormatError: If the file isn't a valid/supported
            `.lockit` container.
        InvalidPasswordOrCorruptedDataError: If `key` is wrong, or any
            chunk's data was corrupted/tampered with.
        TruncatedFileError: If the file ends before its final chunk.
        OperationCancelledError: If `cancel_check` signaled cancellation.
    """
    source = Path(source_path)
    destination = Path(destination_path)
    total_bytes = source.stat().st_size

    try:
        with source.open("rb") as source_file, destination.open("wb") as dest_file:
            header_bytes = source_file.read(HEADER_SIZE_BYTES)
            unpack_header(header_bytes)  # Validates magic; values unused here.
            _read_chunks(
                source_file,
                dest_file,
                key=key,
                total_bytes=total_bytes,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def _read_chunks(
    source_file: BinaryIO,
    dest_file: BinaryIO,
    *,
    key: bytes,
    total_bytes: int,
    progress_callback: ProgressCallback | None,
    cancel_check: CancelCheck | None,
) -> None:
    bytes_processed = HEADER_SIZE_BYTES
    chunk_index = 0
    reached_final_chunk = False

    while True:
        if cancel_check is not None and cancel_check():
            raise OperationCancelledError()

        prefix_bytes = source_file.read(CHUNK_PREFIX_SIZE_BYTES)
        if not prefix_bytes:
            break  # Clean end of file — validated against reached_final_chunk below.

        nonce, is_last, ciphertext_length = unpack_chunk_prefix(prefix_bytes)
        ciphertext = source_file.read(ciphertext_length)

        associated_data = build_chunk_associated_data(chunk_index=chunk_index, is_last=is_last)
        plaintext_chunk = AesGcmCipherEngine.decrypt(ciphertext, key, nonce, associated_data)
        dest_file.write(plaintext_chunk)

        bytes_processed += CHUNK_PREFIX_SIZE_BYTES + len(ciphertext)
        chunk_index += 1

        if progress_callback is not None:
            progress_callback(min(bytes_processed, total_bytes), total_bytes)

        if is_last:
            reached_final_chunk = True
            break

    if not reached_final_chunk:
        raise TruncatedFileError()
