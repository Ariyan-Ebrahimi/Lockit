"""
AES-256-GCM authenticated encryption engine.

GCM (Galois/Counter Mode) is an AEAD (Authenticated Encryption with
Associated Data) mode: it provides both confidentiality (encryption) and
integrity/authenticity (tamper detection) in a single primitive, which is
why LockIt uses it instead of an unauthenticated mode like AES-CBC that
would require bolting on a separate HMAC correctly (a common source of
real-world cryptographic bugs).
"""

from __future__ import annotations

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from core.crypto.constants import AES_KEY_SIZE_BYTES
from core.crypto.exceptions import InvalidKeyMaterialError, InvalidPasswordOrCorruptedDataError


class AesGcmCipherEngine:
    """
    Stateless AES-256-GCM encrypt/decrypt operations.

    This class holds no key material between calls — the key is passed
    explicitly to each method and is the caller's responsibility to wipe
    afterward (see `core.security.secure_memory.SecureBytes`).
    """

    @staticmethod
    def encrypt(
        plaintext: bytes,
        key: bytes,
        nonce: bytes,
        associated_data: bytes | None = None,
    ) -> bytes:
        """
        Encrypt `plaintext` with AES-256-GCM.

        Args:
            plaintext: The raw data to encrypt.
            key: A 32-byte AES-256 key (from `core.crypto.key_derivation.derive_key`).
            nonce: A 12-byte nonce, unique for this key
                (from `core.security.secure_random.generate_nonce`).
            associated_data: Optional data to authenticate but not encrypt
                (e.g. the container header), so tampering with it is also
                detected on decryption.

        Returns:
            Ciphertext with the 16-byte authentication tag appended
            (this is `AESGCM`'s standard output format).

        Raises:
            InvalidKeyMaterialError: If `key` is not exactly 32 bytes.
        """
        AesGcmCipherEngine._validate_key(key)
        aesgcm = AESGCM(key)
        return aesgcm.encrypt(nonce, plaintext, associated_data)

    @staticmethod
    def decrypt(
        ciphertext: bytes,
        key: bytes,
        nonce: bytes,
        associated_data: bytes | None = None,
    ) -> bytes:
        """
        Decrypt and authenticate `ciphertext` produced by `encrypt`.

        Args:
            ciphertext: The encrypted data with its trailing 16-byte tag,
                exactly as returned by `encrypt`.
            key: The same 32-byte AES-256 key used to encrypt.
            nonce: The same 12-byte nonce used to encrypt.
            associated_data: The same associated data (if any) used to encrypt.

        Returns:
            The original plaintext.

        Raises:
            InvalidKeyMaterialError: If `key` is not exactly 32 bytes.
            InvalidPasswordOrCorruptedDataError: If authentication fails —
                meaning either the password (and therefore key) was wrong,
                or the ciphertext/associated data was corrupted or tampered
                with. These two causes are indistinguishable by design.
        """
        AesGcmCipherEngine._validate_key(key)
        aesgcm = AESGCM(key)
        try:
            return aesgcm.decrypt(nonce, ciphertext, associated_data)
        except InvalidTag as exc:
            raise InvalidPasswordOrCorruptedDataError() from exc

    @staticmethod
    def _validate_key(key: bytes) -> None:
        if len(key) != AES_KEY_SIZE_BYTES:
            raise InvalidKeyMaterialError(
                f"AES-256 requires a {AES_KEY_SIZE_BYTES}-byte key, got {len(key)} bytes."
            )
