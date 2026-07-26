"""
Cryptographic parameters for LockIt's encryption engine.

These values define the security posture of every file LockIt encrypts.
Changing them is a breaking-format change for previously encrypted files,
which is why the container format (`core/crypto/container.py`) stores the
iteration count and a format version alongside every encrypted file —
future versions can decrypt old files even if the defaults below change.

References:
- AES-256-GCM: NIST SP 800-38D (authenticated encryption, integrity +
  confidentiality in one primitive; no separate HMAC required).
- PBKDF2-HMAC-SHA256 iteration count: OWASP Password Storage Cheat
  Sheet (2023+) recommends >= 600,000 iterations for PBKDF2-HMAC-SHA256.
"""

from __future__ import annotations

from typing import Final

# --------------------------------------------------------------------------
# AES-256-GCM
# --------------------------------------------------------------------------
AES_KEY_SIZE_BYTES: Final[int] = 32  # 256-bit key
GCM_NONCE_SIZE_BYTES: Final[int] = 12  # 96-bit nonce, the NIST-recommended size for GCM
GCM_TAG_SIZE_BYTES: Final[int] = 16  # 128-bit authentication tag (appended by AESGCM)

# --------------------------------------------------------------------------
# PBKDF2-HMAC-SHA256 key derivation
# --------------------------------------------------------------------------
PBKDF2_SALT_SIZE_BYTES: Final[int] = 16  # 128-bit salt
PBKDF2_DEFAULT_ITERATIONS: Final[int] = 600_000

# --------------------------------------------------------------------------
# .lockit container format
# --------------------------------------------------------------------------
CONTAINER_MAGIC: Final[bytes] = b"LKIT"
CONTAINER_FORMAT_VERSION: Final[int] = 1

# Chunked streaming (used by core/files in Phase 4 for large files)
STREAM_CHUNK_SIZE_BYTES: Final[int] = 4 * 1024 * 1024  # 4 MB
