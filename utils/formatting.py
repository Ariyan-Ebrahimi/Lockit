"""
Human-readable formatting helpers shared by file metadata display,
progress reporting, and (in later phases) the UI's file info panels.
"""

from __future__ import annotations

_SIZE_UNITS = ("B", "KB", "MB", "GB", "TB", "PB")


def format_file_size(size_bytes: int) -> str:
    """
    Format a byte count as a human-readable string (e.g. "4.2 MB").

    Uses base-1024 units, matching how most operating systems report
    file sizes.
    """
    if size_bytes < 0:
        raise ValueError("size_bytes must be non-negative.")

    size = float(size_bytes)
    for unit in _SIZE_UNITS:
        if size < 1024.0 or unit == _SIZE_UNITS[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"  # Unreachable in practice; satisfies type checkers.


def format_duration(seconds: float) -> str:
    """Format a duration in seconds as a compact human-readable string."""
    if seconds < 0:
        raise ValueError("seconds must be non-negative.")

    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    if seconds < 60:
        return f"{seconds:.1f} s"

    minutes, secs = divmod(int(seconds), 60)
    if minutes < 60:
        return f"{minutes}m {secs}s"

    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m"


def format_transfer_rate(bytes_per_second: float) -> str:
    """Format a throughput rate as a human-readable string (e.g. "12.4 MB/s")."""
    return f"{format_file_size(int(bytes_per_second))}/s"
