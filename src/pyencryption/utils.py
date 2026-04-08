"""Utility functions for PyEncryption."""

from __future__ import annotations

import time
from collections.abc import Iterator
from pathlib import Path


def walk_files(directory: Path) -> Iterator[Path]:
    """Recursively yield all file paths in a directory."""
    for item in sorted(directory.rglob("*")):
        if item.is_file():
            yield item


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    for unit in ("KB", "MB", "GB", "TB"):
        size_bytes_f = size_bytes / 1024
        if size_bytes_f < 1024 or unit == "TB":
            return f"{size_bytes_f:.1f} {unit}"
        size_bytes = int(size_bytes_f)
    return f"{size_bytes} B"


def format_duration(seconds: float) -> str:
    """Format duration as human-readable string."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.0f}s"


class Timer:
    """Context manager for timing operations."""

    def __init__(self) -> None:
        self._start: float = 0.0
        self._elapsed: float = 0.0

    def __enter__(self) -> Timer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: object) -> None:
        self._elapsed = time.perf_counter() - self._start

    @property
    def elapsed(self) -> float:
        """Elapsed time in seconds."""
        return self._elapsed
