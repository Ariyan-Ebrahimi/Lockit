"""
Cryptographically secure random generation for LockIt.

All randomness that feeds into encryption (salts, nonces) must come from
the OS's cryptographically secure random number generator — never from
`random`, which is predictable and unsuitable for security purposes.
`os.urandom` is backed by the OS CSPRNG on every platform LockIt targets
(CryptGenRandom/BCryptGenRandom on Windows, /dev/urandom on Linux/macOS),
which is also what `cryptography`'s own internals rely on.
"""

from __future__ import annotations

import os
import secrets

from core.crypto.constants import GCM_NONCE_SIZE_BYTES, PBKDF2_SALT_SIZE_BYTES


def generate_salt(size: int = PBKDF2_SALT_SIZE_BYTES) -> bytes:
    """Generate a cryptographically secure random salt for PBKDF2."""
    return os.urandom(size)


def generate_nonce(size: int = GCM_NONCE_SIZE_BYTES) -> bytes:
    """
    Generate a cryptographically secure random nonce for AES-GCM.

    Critical: a nonce must NEVER be reused with the same key. Since each
    encryption operation derives a fresh key from a fresh random salt,
    nonce reuse across different files is already extremely unlikely;
    generating it randomly here (rather than a counter) keeps the API
    simple and stateless while remaining safe in practice for a
    password-per-file encryption tool.
    """
    return os.urandom(size)


def generate_secure_token(length_bytes: int = 32) -> str:
    """
    Generate a URL-safe random token, useful for things like generating
    a suggested strong password. Not used for key material directly.
    """
    return secrets.token_urlsafe(length_bytes)


def constant_time_compare(a: bytes, b: bytes) -> bool:
    """
    Compare two byte sequences in constant time to avoid timing side
    channels. Prefer this over `a == b` whenever comparing secrets
    (e.g. authentication tags, derived keys) outside of what the
    `cryptography` library already compares internally.
    """
    return secrets.compare_digest(a, b)
