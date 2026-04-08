"""AES-256-GCM encryption engine with PBKDF2 key derivation."""

from __future__ import annotations

import os
import struct
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from pyencryption.crypto.base import (
    DecryptionResult,
    EncryptionResult,
    ProgressCallback,
)
from pyencryption.utils import Timer, walk_files

# File format:
# [MAGIC 4B] [VERSION 1B] [SALT 16B] [NONCE 12B] [CIPHERTEXT...] [GCM TAG 16B]
MAGIC = b"PYEN"
VERSION = 1
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32  # 256-bit
KDF_ITERATIONS = 600_000
HEADER_SIZE = len(MAGIC) + 1 + SALT_SIZE + NONCE_SIZE  # 33 bytes


class AESError(Exception):
    """Raised for AES encryption/decryption errors."""


class AESEngine:
    """AES-256-GCM authenticated encryption with password-based key derivation.

    Produces self-contained .enc files that embed the salt and nonce in the
    header. No separate key file is needed.
    """

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KEY_SIZE,
            salt=salt,
            iterations=KDF_ITERATIONS,
        )
        return kdf.derive(password.encode("utf-8"))

    def encrypt_file(
        self,
        source: Path,
        dest: Path | None = None,
        *,
        password: str | None = None,
    ) -> EncryptionResult:
        if password is None:
            raise AESError("Password is required for AES encryption")

        source = Path(source)
        if not source.is_file():
            raise FileNotFoundError(f"Source file not found: {source}")

        if dest is None:
            dest = source.with_suffix(source.suffix + ".enc")

        with Timer() as t:
            plaintext = source.read_bytes()
            salt = os.urandom(SALT_SIZE)
            nonce = os.urandom(NONCE_SIZE)
            key = self._derive_key(password, salt)
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)

            header = MAGIC + struct.pack("B", VERSION) + salt + nonce
            dest.write_bytes(header + ciphertext)

        return EncryptionResult(
            ciphertext_path=dest,
            elapsed_seconds=t.elapsed,
        )

    def decrypt_file(
        self,
        source: Path,
        dest: Path | None = None,
        *,
        password: str | None = None,
    ) -> DecryptionResult:
        if password is None:
            raise AESError("Password is required for AES decryption")

        source = Path(source)
        if not source.is_file():
            raise FileNotFoundError(f"Encrypted file not found: {source}")

        if dest is None:
            name = source.name
            if name.endswith(".enc"):
                name = name[: -len(".enc")]
            else:
                name = "decrypted_" + name
            dest = source.with_name(name)

        with Timer() as t:
            data = source.read_bytes()

            if len(data) < HEADER_SIZE:
                raise AESError("File is too small to be a valid encrypted file")

            magic = data[:4]
            if magic != MAGIC:
                raise AESError(
                    f"Invalid file format (expected magic {MAGIC!r}, got {magic!r})"
                )

            version = data[4]
            if version != VERSION:
                raise AESError(f"Unsupported format version: {version}")

            salt = data[5 : 5 + SALT_SIZE]
            nonce = data[5 + SALT_SIZE : 5 + SALT_SIZE + NONCE_SIZE]
            ciphertext = data[HEADER_SIZE:]

            key = self._derive_key(password, salt)
            aesgcm = AESGCM(key)

            try:
                plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            except Exception as e:
                raise AESError(
                    "Decryption failed. Wrong password or tampered file."
                ) from e

            dest.write_bytes(plaintext)

        return DecryptionResult(
            plaintext_path=dest,
            elapsed_seconds=t.elapsed,
        )

    def encrypt_folder(
        self,
        source_dir: Path,
        dest_dir: Path | None = None,
        *,
        password: str | None = None,
        progress: ProgressCallback | None = None,
    ) -> EncryptionResult:
        if password is None:
            raise AESError("Password is required for AES encryption")

        source_dir = Path(source_dir)
        if not source_dir.is_dir():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")

        if dest_dir is None:
            dest_dir = source_dir.with_name(source_dir.name + "_encrypted")

        files = list(walk_files(source_dir))
        total = len(files)

        with Timer() as t:
            for i, file_path in enumerate(files):
                relative = file_path.relative_to(source_dir)
                out_path = dest_dir / relative.with_suffix(
                    relative.suffix + ".enc"
                )
                out_path.parent.mkdir(parents=True, exist_ok=True)

                if progress:
                    progress(i + 1, total, file_path.name)

                self.encrypt_file(file_path, out_path, password=password)

        return EncryptionResult(
            ciphertext_path=dest_dir,
            elapsed_seconds=t.elapsed,
        )

    def decrypt_folder(
        self,
        source_dir: Path,
        dest_dir: Path | None = None,
        *,
        password: str | None = None,
        progress: ProgressCallback | None = None,
    ) -> DecryptionResult:
        if password is None:
            raise AESError("Password is required for AES decryption")

        source_dir = Path(source_dir)
        if not source_dir.is_dir():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")

        if dest_dir is None:
            dest_dir = source_dir.with_name(source_dir.name + "_decrypted")

        files = list(walk_files(source_dir))
        total = len(files)

        with Timer() as t:
            for i, file_path in enumerate(files):
                relative = file_path.relative_to(source_dir)
                name = relative.name
                if name.endswith(".enc"):
                    name = name[: -len(".enc")]
                out_path = dest_dir / relative.with_name(name)
                out_path.parent.mkdir(parents=True, exist_ok=True)

                if progress:
                    progress(i + 1, total, file_path.name)

                self.decrypt_file(file_path, out_path, password=password)

        return DecryptionResult(
            plaintext_path=dest_dir,
            elapsed_seconds=t.elapsed,
        )
