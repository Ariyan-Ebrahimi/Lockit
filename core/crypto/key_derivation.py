"""
Password-based key derivation for LockIt, using PBKDF2-HMAC-SHA256.

A user's password is never used directly as an AES key: it is run
through PBKDF2 with a random salt and a high iteration count, which
makes brute-force and rainbow-table attacks computationally expensive
even if an attacker obtains the encrypted file.
"""

from __future__ import annotations

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config.constants import TEXT_ENCODING
from core.crypto.constants import AES_KEY_SIZE_BYTES, PBKDF2_DEFAULT_ITERATIONS


def derive_key(
    password: str,
    salt: bytes,
    iterations: int = PBKDF2_DEFAULT_ITERATIONS,
    key_size_bytes: int = AES_KEY_SIZE_BYTES,
) -> bytes:
    """
    Derive an AES-256 key from a user password using PBKDF2-HMAC-SHA256.

    Args:
        password: The user's plaintext password. Never logged, never
            stored — used only transiently to compute the key.
        salt: A unique, random, per-file salt (see
            `core.security.secure_random.generate_salt`). Reusing a salt
            across files/passwords weakens the guarantee that identical
            passwords produce unrelated keys.
        iterations: PBKDF2 iteration count. Must be stored alongside the
            encrypted file (see `core.crypto.container`) so decryption
            can reproduce the exact same key later, even if LockIt's
            default iteration count changes in a future version.
        key_size_bytes: Output key length; 32 bytes for AES-256.

    Returns:
        A `key_size_bytes`-length key suitable for AES-256-GCM.

    Raises:
        ValueError: If `password` is empty or `salt` is empty — both are
            programming errors that should never reach this function
            (the UI/validators layer is responsible for rejecting empty
            passwords before encryption is attempted).
    """
    if not password:
        raise ValueError("Password must not be empty.")
    if not salt:
        raise ValueError("Salt must not be empty.")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_size_bytes,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode(TEXT_ENCODING))
