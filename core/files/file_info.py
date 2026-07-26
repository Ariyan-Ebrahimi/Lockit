"""
File metadata extraction for LockIt.

Used by the file browser / drag-and-drop widgets to display size, type,
and modification time before a user commits to encrypting or decrypting
a file, and by the container writer/reader to size progress reporting.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from config.constants import ENCRYPTED_FILE_EXTENSION
from utils.formatting import format_file_size


@dataclass(frozen=True, slots=True)
class FileInfo:
    """Snapshot of a file's metadata at the moment it was inspected."""

    path: Path
    name: str
    extension: str
    size_bytes: int
    modified_at: datetime
    is_encrypted_container: bool

    @property
    def size_display(self) -> str:
        """Human-readable file size, e.g. '4.2 MB'."""
        return format_file_size(self.size_bytes)

    @property
    def modified_display(self) -> str:
        """Human-readable last-modified timestamp."""
        return self.modified_at.strftime("%b %d, %Y at %H:%M")


def get_file_info(path: str | Path) -> FileInfo:
    """
    Inspect a file on disk and return its metadata.

    Args:
        path: Path to an existing, readable file.

    Returns:
        A populated `FileInfo`.

    Raises:
        FileNotFoundError: If `path` does not exist.
        IsADirectoryError: If `path` points to a directory, not a file.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if file_path.is_dir():
        raise IsADirectoryError(f"Expected a file, got a directory: {file_path}")

    stat_result = file_path.stat()

    return FileInfo(
        path=file_path,
        name=file_path.name,
        extension=file_path.suffix,
        size_bytes=stat_result.st_size,
        modified_at=datetime.fromtimestamp(stat_result.st_mtime),
        is_encrypted_container=file_path.suffix == ENCRYPTED_FILE_EXTENSION,
    )


def suggest_encrypted_output_path(source_path: str | Path) -> Path:
    """Suggest an output path for encrypting `source_path` (appends `.lockit`)."""
    source = Path(source_path)
    return source.with_name(source.name + ENCRYPTED_FILE_EXTENSION)


def suggest_decrypted_output_path(source_path: str | Path) -> Path:
    """
    Suggest an output path for decrypting `source_path`.

    Strips a trailing `.lockit` extension if present; otherwise appends
    `.decrypted` to the original name so a decrypted file never silently
    overwrites something with an unexpected name.
    """
    source = Path(source_path)
    if source.suffix == ENCRYPTED_FILE_EXTENSION:
        return source.with_suffix("")
    return source.with_name(source.name + ".decrypted")
