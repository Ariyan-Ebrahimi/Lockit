"""
The `.lockit` container binary format.

Layout of an encrypted `.lockit` file:

    +----------------------------------------------------------+
    | MAGIC (4 bytes)            = b"LKIT"                     |
    | FORMAT_VERSION (1 byte)    = 1                            |
    | KDF_ITERATIONS (4 bytes)   = big-endian uint32             |
    | SALT (16 bytes)             = PBKDF2 salt                  |
    +----------------------------------------------------------+
    | CHUNK 0                                                    |
    |   NONCE (12 bytes)                                         |
    |   IS_LAST (1 byte)          = 0x00 or 0x01                 |
    |   CIPHERTEXT_LENGTH (4 bytes) = big-endian uint32           |
    |   CIPHERTEXT (variable)     = AES-256-GCM(plaintext) + tag  |
    +----------------------------------------------------------+
    | CHUNK 1 ...                                                |
    +----------------------------------------------------------+
    | ... final chunk has IS_LAST = 0x01                         |
    +----------------------------------------------------------+

Each chunk is encrypted independently with a fresh random nonce and
authenticated with associated data binding it to its position in the
stream (`chunk_index` + `is_last`), so chunks cannot be silently
reordered, duplicated, or dropped from the middle without breaking
authentication. A missing *final* chunk (i.e. the file is cut off before
any chunk with `IS_LAST = 1` was read) is detected separately by the
reader as a truncation error, since AEAD alone cannot distinguish "the
stream legitimately ended" from "the stream was cut short."

Storing `KDF_ITERATIONS` and `FORMAT_VERSION` per-file (rather than
relying on the current build's defaults) means a future LockIt version
can raise the default iteration count without breaking decryption of
files created by older versions.
"""

from __future__ import annotations

import struct

from core.crypto.constants import (
    CONTAINER_FORMAT_VERSION,
    CONTAINER_MAGIC,
    GCM_NONCE_SIZE_BYTES,
    PBKDF2_SALT_SIZE_BYTES,
)

# Header: magic (4s) + version (B) + iterations (I) + salt (16s)
_HEADER_STRUCT = struct.Struct(f">4sBI{PBKDF2_SALT_SIZE_BYTES}s")
HEADER_SIZE_BYTES = _HEADER_STRUCT.size

# Chunk prefix: nonce (12s) + is_last (B) + ciphertext_length (I)
_CHUNK_PREFIX_STRUCT = struct.Struct(f">{GCM_NONCE_SIZE_BYTES}sBI")
CHUNK_PREFIX_SIZE_BYTES = _CHUNK_PREFIX_STRUCT.size


def pack_header(*, iterations: int, salt: bytes) -> bytes:
    """Serialize the container header (magic, version, KDF params, salt)."""
    if len(salt) != PBKDF2_SALT_SIZE_BYTES:
        raise ValueError(f"Salt must be {PBKDF2_SALT_SIZE_BYTES} bytes, got {len(salt)}.")
    return _HEADER_STRUCT.pack(CONTAINER_MAGIC, CONTAINER_FORMAT_VERSION, iterations, salt)


def unpack_header(data: bytes) -> tuple[int, int, bytes]:
    """
    Deserialize a container header.

    Returns:
        A tuple of (format_version, iterations, salt).

    Raises:
        ValueError: If `data` is too short or the magic bytes don't match.
    """
    if len(data) < HEADER_SIZE_BYTES:
        raise ValueError("Data too short to contain a valid LockIt header.")

    magic, version, iterations, salt = _HEADER_STRUCT.unpack(data[:HEADER_SIZE_BYTES])
    if magic != CONTAINER_MAGIC:
        raise ValueError("Not a LockIt (.lockit) file: magic bytes do not match.")

    return version, iterations, salt


def pack_chunk_prefix(*, nonce: bytes, is_last: bool, ciphertext_length: int) -> bytes:
    """Serialize the fixed-size prefix that precedes each chunk's ciphertext."""
    if len(nonce) != GCM_NONCE_SIZE_BYTES:
        raise ValueError(f"Nonce must be {GCM_NONCE_SIZE_BYTES} bytes, got {len(nonce)}.")
    return _CHUNK_PREFIX_STRUCT.pack(nonce, 1 if is_last else 0, ciphertext_length)


def unpack_chunk_prefix(data: bytes) -> tuple[bytes, bool, int]:
    """
    Deserialize a chunk prefix.

    Returns:
        A tuple of (nonce, is_last, ciphertext_length).
    """
    if len(data) < CHUNK_PREFIX_SIZE_BYTES:
        raise ValueError("Data too short to contain a valid chunk prefix.")

    nonce, is_last_byte, ciphertext_length = _CHUNK_PREFIX_STRUCT.unpack(
        data[:CHUNK_PREFIX_SIZE_BYTES]
    )
    return nonce, bool(is_last_byte), ciphertext_length


def build_chunk_associated_data(*, chunk_index: int, is_last: bool) -> bytes:
    """
    Build the associated data authenticated (but not encrypted) alongside
    a chunk's ciphertext, binding it to its position in the stream.
    """
    return chunk_index.to_bytes(8, "big") + (b"\x01" if is_last else b"\x00")
