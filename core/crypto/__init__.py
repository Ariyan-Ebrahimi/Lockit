"""
Public API for LockIt's cryptographic core.

Import from `core.crypto` directly (e.g. `from core.crypto import
AesGcmCipherEngine, derive_key`) rather than reaching into submodules,
so the internal file layout can change without breaking callers.
"""

from __future__ import annotations

from core.crypto.cipher_engine import AesGcmCipherEngine
from core.crypto.constants import (
    AES_KEY_SIZE_BYTES,
    GCM_NONCE_SIZE_BYTES,
    GCM_TAG_SIZE_BYTES,
    PBKDF2_DEFAULT_ITERATIONS,
    PBKDF2_SALT_SIZE_BYTES,
)
from core.crypto.exceptions import (
    CryptoError,
    InvalidKeyMaterialError,
    InvalidPasswordOrCorruptedDataError,
    TruncatedFileError,
    UnsupportedFileFormatError,
)
from core.crypto.key_derivation import derive_key

__all__ = [
    "AesGcmCipherEngine",
    "derive_key",
    "AES_KEY_SIZE_BYTES",
    "GCM_NONCE_SIZE_BYTES",
    "GCM_TAG_SIZE_BYTES",
    "PBKDF2_DEFAULT_ITERATIONS",
    "PBKDF2_SALT_SIZE_BYTES",
    "CryptoError",
    "InvalidKeyMaterialError",
    "InvalidPasswordOrCorruptedDataError",
    "TruncatedFileError",
    "UnsupportedFileFormatError",
]
