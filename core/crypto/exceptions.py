"""
Exception hierarchy for LockIt's cryptographic backend.

Using dedicated exception types (rather than letting raw `ValueError` /
`InvalidTag` propagate) lets the UI layer (Phase 5) present accurate,
specific messages to the user without depending on `cryptography`
internals, and lets tests assert on precise failure modes.
"""

from __future__ import annotations


class CryptoError(Exception):
    """Base class for all cryptographic errors raised by LockIt."""


class InvalidPasswordOrCorruptedDataError(CryptoError):
    """
    Raised when AES-GCM authentication fails during decryption.

    This is intentionally a single error type covering both an incorrect
    password and tampered/corrupted ciphertext: AEAD authentication
    failure cannot distinguish between the two, and revealing which one
    occurred would leak information useful to an attacker.
    """

    def __init__(self) -> None:
        super().__init__(
            "Decryption failed: the password is incorrect, or the file is "
            "corrupted or has been tampered with."
        )


class UnsupportedFileFormatError(CryptoError):
    """Raised when a file is not a recognized `.lockit` container, or its
    format version is newer than this build of LockIt supports."""


class InvalidKeyMaterialError(CryptoError):
    """Raised when a derived key or provided key does not match the
    expected size for AES-256 (a programming error, not a user error)."""


class TruncatedFileError(CryptoError):
    """
    Raised when a `.lockit` container ends before its final chunk marker
    was decrypted — i.e. the file was cut short (accidentally or by
    tampering) after the point authentication would normally catch.
    """

    def __init__(self) -> None:
        super().__init__(
            "This file appears to be incomplete or truncated. It may not "
            "have finished copying, or it has been damaged."
        )
