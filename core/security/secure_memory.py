"""
Secure memory handling utilities.

CPython cannot guarantee that memory is wiped the instant an object is
garbage collected, and immutable `bytes`/`str` objects cannot be
overwritten in place at all — a `str` password or a `bytes` key may
leave copies in memory until the interpreter reuses that memory. This
module provides best-effort mitigations:

1. `SecureBytes` wraps key material in a mutable `bytearray` so it CAN
   be explicitly zeroed out the moment it's no longer needed, rather
   than waiting on garbage collection.
2. `wipe_bytearray` performs the actual in-place zeroing.

This is a defense-in-depth measure, not an absolute guarantee — Python's
memory model means some copies (e.g. from intermediate operations) may
still exist until overwritten by later allocations. True secure memory
(mlock'd, non-swappable pages) is outside what a pure-Python application
can guarantee cross-platform.
"""

from __future__ import annotations

from types import TracebackType


def wipe_bytearray(data: bytearray) -> None:
    """Overwrite every byte of a mutable buffer with zeros, in place."""
    for i in range(len(data)):
        data[i] = 0


class SecureBytes:
    """
    A context manager that holds sensitive byte material (e.g. a derived
    AES key) in a mutable buffer and guarantees it is zeroed out when the
    `with` block exits, whether normally or via an exception.

    Example:
        with SecureBytes(derive_key(password, salt)) as key:
            cipher_engine.encrypt(plaintext, key.data)
        # `key`'s underlying buffer is now zeroed.
    """

    __slots__ = ("_buffer", "_wiped")

    def __init__(self, initial: bytes | bytearray) -> None:
        self._buffer = bytearray(initial)
        self._wiped = False

    @property
    def data(self) -> bytes:
        """Return an immutable snapshot of the current buffer contents.

        Note: this necessarily creates a `bytes` copy, since most crypto
        APIs (including `cryptography`) require `bytes`. The copy exists
        only as long as the caller holds a reference to it.
        """
        if self._wiped:
            raise ValueError("Cannot read SecureBytes after it has been wiped.")
        return bytes(self._buffer)

    def wipe(self) -> None:
        """Zero out the underlying buffer immediately."""
        if not self._wiped:
            wipe_bytearray(self._buffer)
            self._wiped = True

    def __enter__(self) -> "SecureBytes":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.wipe()

    def __len__(self) -> int:
        return len(self._buffer)

    def __repr__(self) -> str:
        # Never include the actual bytes in a repr — logs/debuggers may
        # capture repr() output.
        state = "wiped" if self._wiped else f"{len(self._buffer)} bytes"
        return f"<SecureBytes: {state}>"
