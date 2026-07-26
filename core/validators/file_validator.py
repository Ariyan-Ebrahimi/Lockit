"""
File path validation for LockIt.

Runs before any file is read for encryption/decryption or written to
disk, so failures produce a clear message instead of a raw OS exception,
and so an existing file is never silently overwritten.
"""

from __future__ import annotations

import os
from pathlib import Path

from core.validators.exceptions import ValidationError

# Defends the UI from attempting to load absurdly large files into a
# progress-tracked operation without at least warning the user first.
# This is a soft ceiling, not a hard technical limit — the streaming
# container format (Phase 4) has no inherent file-size restriction.
MAX_RECOMMENDED_FILE_SIZE_BYTES = 10 * 1024 * 1024 * 1024  # 10 GB


def validate_input_file(path: str | Path) -> Path:
    """
    Validate that `path` refers to a real, non-empty, readable file.

    Args:
        path: Candidate input file path.

    Returns:
        The validated path, resolved to an absolute `Path`.

    Raises:
        ValidationError: If the path does not exist, is a directory,
            is empty, or is not readable.
    """
    file_path = Path(path).expanduser().resolve()

    if not file_path.exists():
        raise ValidationError(f"File does not exist: {file_path.name}")

    if file_path.is_dir():
        raise ValidationError(f"'{file_path.name}' is a folder, not a file.")

    if not os.access(file_path, os.R_OK):
        raise ValidationError(f"File is not readable: {file_path.name}")

    if file_path.stat().st_size == 0:
        raise ValidationError(f"'{file_path.name}' is empty and cannot be encrypted.")

    return file_path


def is_oversized(path: str | Path) -> bool:
    """Whether a file exceeds the soft recommended size ceiling (informational only)."""
    return Path(path).stat().st_size > MAX_RECOMMENDED_FILE_SIZE_BYTES


def validate_output_path(path: str | Path, *, allow_overwrite: bool = False) -> Path:
    """
    Validate that `path` is a safe destination to write a new file to.

    Args:
        path: Candidate output file path.
        allow_overwrite: When False (the default), raises if a file
            already exists at `path` — the UI must obtain explicit user
            confirmation before retrying with `allow_overwrite=True`.

    Returns:
        The validated path, resolved to an absolute `Path`.

    Raises:
        ValidationError: If the parent directory doesn't exist, isn't
            writable, or the destination file exists and overwriting
            was not explicitly allowed.
    """
    output_path = Path(path).expanduser().resolve()
    parent_dir = output_path.parent

    if not parent_dir.exists():
        raise ValidationError(f"Destination folder does not exist: {parent_dir}")

    if not os.access(parent_dir, os.W_OK):
        raise ValidationError(f"Destination folder is not writable: {parent_dir}")

    if output_path.exists() and not allow_overwrite:
        raise ValidationError(
            f"A file named '{output_path.name}' already exists at this location."
        )

    return output_path
