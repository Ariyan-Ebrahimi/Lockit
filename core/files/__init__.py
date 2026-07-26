"""
Public API for LockIt's file management layer: metadata extraction and
the streaming `.lockit` container format (encryption/decryption).
"""

from __future__ import annotations

from core.files.container_reader import decrypt_container_to_file, read_container_header
from core.files.container_writer import encrypt_file_to_container
from core.files.exceptions import OperationCancelledError
from core.files.file_info import (
    FileInfo,
    get_file_info,
    suggest_decrypted_output_path,
    suggest_encrypted_output_path,
)

__all__ = [
    "encrypt_file_to_container",
    "decrypt_container_to_file",
    "read_container_header",
    "OperationCancelledError",
    "FileInfo",
    "get_file_info",
    "suggest_encrypted_output_path",
    "suggest_decrypted_output_path",
]
