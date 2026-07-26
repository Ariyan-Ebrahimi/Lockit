"""
`CryptoWorker` — a `QThread` subclass that runs an encrypt or decrypt
service call in the background, emitting typed Qt signals for progress,
success, and failure so the UI thread never blocks.

Signal contract (always emitted from the worker thread; connect with
`Qt.ConnectionType.QueuedConnection` or let Qt auto-detect):

  progress_updated(int, int)  — (bytes_done, total_bytes)
  operation_completed(object) — EncryptionResult | DecryptionResult
  operation_failed(str, str)  — (error_title, error_detail)
  operation_cancelled()       — emitted when cancel was honoured

Cancellation is cooperative: the UI calls `request_cancel()` which sets
a thread-safe flag checked between chunks by the container writer/reader.
"""

from __future__ import annotations

import threading
from enum import Enum, auto
from pathlib import Path
from typing import Union

from PySide6.QtCore import QThread, Signal

from core.crypto.exceptions import (
    CryptoError,
    InvalidPasswordOrCorruptedDataError,
    TruncatedFileError,
    UnsupportedFileFormatError,
)
from core.files.exceptions import OperationCancelledError
from core.validators.exceptions import ValidationError
from services.decryption_service import DecryptionResult, DecryptionService
from services.encryption_service import EncryptionResult, EncryptionService
from utils.logger import get_logger

logger = get_logger()

OperationResult = Union[EncryptionResult, DecryptionResult]


class OperationKind(Enum):
    ENCRYPT = auto()
    DECRYPT = auto()


class CryptoWorker(QThread):
    """Background worker for a single encrypt or decrypt operation."""

    progress_updated = Signal(int, int)       # bytes_done, total_bytes
    operation_completed = Signal(object)       # EncryptionResult | DecryptionResult
    operation_failed = Signal(str, str)        # title, detail
    operation_cancelled = Signal()

    def __init__(
        self,
        *,
        kind: OperationKind,
        source_path: str | Path,
        password: str,
        output_path: str | Path | None = None,
        allow_overwrite: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._kind = kind
        self._source_path = source_path
        self._password = password
        self._output_path = output_path
        self._allow_overwrite = allow_overwrite
        self._cancel_flag = threading.Event()

    # ------------------------------------------------------------------
    # Public control API (called from UI thread)
    # ------------------------------------------------------------------

    def request_cancel(self) -> None:
        """Signal the worker to stop at the next chunk boundary."""
        self._cancel_flag.set()

    # ------------------------------------------------------------------
    # QThread entry point
    # ------------------------------------------------------------------

    def run(self) -> None:  # noqa: N802 (Qt override)
        try:
            if self._kind == OperationKind.ENCRYPT:
                result = self._run_encrypt()
            else:
                result = self._run_decrypt()
            self.operation_completed.emit(result)
        except OperationCancelledError:
            logger.info("Operation cancelled by user.")
            self.operation_cancelled.emit()
        except ValidationError as exc:
            self.operation_failed.emit("Invalid Input", str(exc))
        except InvalidPasswordOrCorruptedDataError:
            self.operation_failed.emit(
                "Wrong Password or Corrupted File",
                "The password is incorrect, or the file has been damaged or tampered with.",
            )
        except TruncatedFileError as exc:
            self.operation_failed.emit("Incomplete File", str(exc))
        except UnsupportedFileFormatError as exc:
            self.operation_failed.emit("Unsupported File", str(exc))
        except CryptoError as exc:
            logger.exception("Unexpected crypto error.")
            self.operation_failed.emit("Encryption Error", str(exc))
        except OSError as exc:
            logger.exception("I/O error during operation.")
            self.operation_failed.emit("File Error", str(exc))
        except Exception:
            logger.exception("Unexpected error in CryptoWorker.")
            self.operation_failed.emit(
                "Unexpected Error",
                "An unexpected error occurred. Please check the log for details.",
            )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _cancel_check(self) -> bool:
        return self._cancel_flag.is_set()

    def _progress_callback(self, bytes_done: int, total_bytes: int) -> None:
        self.progress_updated.emit(bytes_done, total_bytes)

    def _run_encrypt(self) -> EncryptionResult:
        service = EncryptionService()
        return service.encrypt(
            self._source_path,
            self._password,
            output_path=self._output_path,
            allow_overwrite=self._allow_overwrite,
            progress_callback=self._progress_callback,
            cancel_check=self._cancel_check,
        )

    def _run_decrypt(self) -> DecryptionResult:
        service = DecryptionService()
        return service.decrypt(
            self._source_path,
            self._password,
            output_path=self._output_path,
            allow_overwrite=self._allow_overwrite,
            progress_callback=self._progress_callback,
            cancel_check=self._cancel_check,
        )
