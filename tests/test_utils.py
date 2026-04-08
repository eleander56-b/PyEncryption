"""Tests for pyencryption.utils."""

from __future__ import annotations

import time
from pathlib import Path

from pyencryption.utils import Timer, format_duration, format_size, walk_files


class TestWalkFiles:
    def test_yields_files_not_directories(self, tmp_path: Path) -> None:
        (tmp_path / "dir").mkdir()
        (tmp_path / "dir" / "file.txt").write_text("hello")
        (tmp_path / "root.txt").write_text("world")

        result = list(walk_files(tmp_path))
        assert all(f.is_file() for f in result)
        assert len(result) == 2

    def test_recursive(self, tmp_path: Path) -> None:
        (tmp_path / "a" / "b").mkdir(parents=True)
        (tmp_path / "a" / "b" / "deep.txt").write_text("deep")
        result = list(walk_files(tmp_path))
        assert len(result) == 1
        assert result[0].name == "deep.txt"

    def test_empty_directory(self, tmp_path: Path) -> None:
        assert list(walk_files(tmp_path)) == []


class TestFormatSize:
    def test_bytes(self) -> None:
        assert format_size(500) == "500 B"

    def test_kilobytes(self) -> None:
        assert format_size(2048) == "2.0 KB"

    def test_megabytes(self) -> None:
        assert format_size(5 * 1024 * 1024) == "5.0 MB"

    def test_gigabytes(self) -> None:
        assert format_size(3 * 1024 * 1024 * 1024) == "3.0 GB"


class TestFormatDuration:
    def test_milliseconds(self) -> None:
        assert format_duration(0.5) == "500ms"

    def test_seconds(self) -> None:
        assert format_duration(5.3) == "5.3s"

    def test_minutes(self) -> None:
        assert format_duration(125.0) == "2m 5s"


class TestTimer:
    def test_elapsed_is_positive(self) -> None:
        with Timer() as t:
            time.sleep(0.01)
        assert t.elapsed > 0

    def test_elapsed_is_reasonable(self) -> None:
        with Timer() as t:
            time.sleep(0.05)
        assert 0.03 < t.elapsed < 0.5
