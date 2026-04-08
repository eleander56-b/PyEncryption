"""Shared test fixtures for PyEncryption."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture
def tmp_file(tmp_path: Path) -> Path:
    """Create a temporary file with known content."""
    f = tmp_path / "testfile.txt"
    f.write_bytes(b"Hello, World! This is test content for encryption.")
    return f


@pytest.fixture
def tmp_folder(tmp_path: Path) -> Path:
    """Create a temporary folder structure with multiple files."""
    (tmp_path / "sub1").mkdir()
    (tmp_path / "sub1" / "a.txt").write_bytes(b"File A content")
    (tmp_path / "sub1" / "b.bin").write_bytes(os.urandom(1024))
    (tmp_path / "sub2").mkdir()
    (tmp_path / "sub2" / "c.txt").write_bytes(b"File C content")
    return tmp_path


@pytest.fixture
def password() -> str:
    return "test-password-123!"
