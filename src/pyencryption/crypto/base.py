"""Base types and protocol for encryption engines."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass
class EncryptionResult:
    """Result of an encryption operation."""

    ciphertext_path: Path
    elapsed_seconds: float


@dataclass
class DecryptionResult:
    """Result of a decryption operation."""

    plaintext_path: Path
    elapsed_seconds: float


ProgressCallback = Callable[[int, int, str], None]
"""Callback(current, total, filename) for progress reporting."""


@runtime_checkable
class CryptoEngine(Protocol):
    """Protocol that all encryption backends must satisfy."""

    def encrypt_file(
        self,
        source: Path,
        dest: Path | None = None,
        *,
        password: str | None = None,
    ) -> EncryptionResult: ...

    def decrypt_file(
        self,
        source: Path,
        dest: Path | None = None,
        *,
        password: str | None = None,
    ) -> DecryptionResult: ...

    def encrypt_folder(
        self,
        source_dir: Path,
        dest_dir: Path | None = None,
        *,
        password: str | None = None,
        progress: ProgressCallback | None = None,
    ) -> EncryptionResult: ...

    def decrypt_folder(
        self,
        source_dir: Path,
        dest_dir: Path | None = None,
        *,
        password: str | None = None,
        progress: ProgressCallback | None = None,
    ) -> DecryptionResult: ...
