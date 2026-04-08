"""Tests for AES-256-GCM encryption engine."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from pyencryption.crypto.aes import HEADER_SIZE, MAGIC, VERSION, AESEngine, AESError


@pytest.fixture
def engine() -> AESEngine:
    return AESEngine()


class TestAESEncryptDecrypt:
    def test_roundtrip(self, engine: AESEngine, tmp_file: Path, password: str) -> None:
        original = tmp_file.read_bytes()
        result = engine.encrypt_file(tmp_file, password=password)

        assert result.ciphertext_path.exists()
        assert result.ciphertext_path != tmp_file
        assert result.elapsed_seconds > 0

        dec_result = engine.decrypt_file(result.ciphertext_path, password=password)
        assert dec_result.plaintext_path.read_bytes() == original

    def test_encrypt_creates_enc_file(
        self, engine: AESEngine, tmp_file: Path, password: str
    ) -> None:
        original = tmp_file.read_bytes()
        result = engine.encrypt_file(tmp_file, password=password)

        assert result.ciphertext_path.suffix == ".enc"
        assert tmp_file.read_bytes() == original  # original untouched

    def test_wrong_password_raises(
        self, engine: AESEngine, tmp_file: Path, password: str
    ) -> None:
        result = engine.encrypt_file(tmp_file, password=password)
        with pytest.raises(AESError, match="Wrong password or tampered"):
            engine.decrypt_file(result.ciphertext_path, password="wrong-password")

    def test_encrypted_file_has_correct_header(
        self, engine: AESEngine, tmp_file: Path, password: str
    ) -> None:
        result = engine.encrypt_file(tmp_file, password=password)
        data = result.ciphertext_path.read_bytes()

        assert data[:4] == MAGIC
        assert data[4] == VERSION
        assert len(data) >= HEADER_SIZE

    def test_empty_file(self, engine: AESEngine, tmp_path: Path, password: str) -> None:
        empty = tmp_path / "empty.txt"
        empty.write_bytes(b"")

        result = engine.encrypt_file(empty, password=password)
        dec = engine.decrypt_file(result.ciphertext_path, password=password)
        assert dec.plaintext_path.read_bytes() == b""

    def test_large_file(self, engine: AESEngine, tmp_path: Path, password: str) -> None:
        large = tmp_path / "large.bin"
        content = os.urandom(1024 * 1024)  # 1MB
        large.write_bytes(content)

        result = engine.encrypt_file(large, password=password)
        dec = engine.decrypt_file(result.ciphertext_path, password=password)
        assert dec.plaintext_path.read_bytes() == content

    def test_tampered_ciphertext_raises(
        self, engine: AESEngine, tmp_file: Path, password: str
    ) -> None:
        result = engine.encrypt_file(tmp_file, password=password)
        data = bytearray(result.ciphertext_path.read_bytes())
        # Flip a byte in the ciphertext area (after header)
        data[HEADER_SIZE + 1] ^= 0xFF
        result.ciphertext_path.write_bytes(bytes(data))

        with pytest.raises(AESError, match="Wrong password or tampered"):
            engine.decrypt_file(result.ciphertext_path, password=password)

    def test_different_passwords_different_ciphertext(
        self, engine: AESEngine, tmp_path: Path
    ) -> None:
        f1 = tmp_path / "f1.txt"
        f2 = tmp_path / "f2.txt"
        content = b"identical content"
        f1.write_bytes(content)
        f2.write_bytes(content)

        r1 = engine.encrypt_file(f1, password="password-a")
        r2 = engine.encrypt_file(f2, password="password-b")

        assert r1.ciphertext_path.read_bytes() != r2.ciphertext_path.read_bytes()

    def test_nondeterministic_encryption(
        self, engine: AESEngine, tmp_path: Path, password: str
    ) -> None:
        f1 = tmp_path / "f1.txt"
        f2 = tmp_path / "f2.txt"
        content = b"same content each time"
        f1.write_bytes(content)
        f2.write_bytes(content)

        r1 = engine.encrypt_file(f1, password=password)
        r2 = engine.encrypt_file(f2, password=password)

        # Different salt/nonce each time -> different ciphertext
        assert r1.ciphertext_path.read_bytes() != r2.ciphertext_path.read_bytes()

    def test_file_not_found(self, engine: AESEngine, tmp_path: Path, password: str) -> None:
        with pytest.raises(FileNotFoundError):
            engine.encrypt_file(tmp_path / "nonexistent.txt", password=password)

    def test_no_password_raises(self, engine: AESEngine, tmp_file: Path) -> None:
        with pytest.raises(AESError, match="Password is required"):
            engine.encrypt_file(tmp_file)

    def test_custom_dest(
        self, engine: AESEngine, tmp_file: Path, tmp_path: Path, password: str
    ) -> None:
        dest = tmp_path / "custom_output.enc"
        result = engine.encrypt_file(tmp_file, dest=dest, password=password)
        assert result.ciphertext_path == dest
        assert dest.exists()

    def test_too_small_file_raises(
        self, engine: AESEngine, tmp_path: Path, password: str
    ) -> None:
        small = tmp_path / "small.enc"
        small.write_bytes(b"tiny")
        with pytest.raises(AESError, match="too small"):
            engine.decrypt_file(small, password=password)

    def test_bad_magic_raises(
        self, engine: AESEngine, tmp_path: Path, password: str
    ) -> None:
        bad = tmp_path / "bad.enc"
        bad.write_bytes(b"XXXX" + b"\x00" * 50)
        with pytest.raises(AESError, match="Invalid file format"):
            engine.decrypt_file(bad, password=password)


class TestAESFolderOperations:
    def test_encrypt_folder_roundtrip(
        self, engine: AESEngine, tmp_folder: Path, tmp_path: Path, password: str
    ) -> None:
        # Collect original content
        original_files: dict[str, bytes] = {}
        for f in tmp_folder.rglob("*"):
            if f.is_file():
                original_files[str(f.relative_to(tmp_folder))] = f.read_bytes()

        enc_dir = tmp_path / "encrypted"
        dec_dir = tmp_path / "decrypted"

        engine.encrypt_folder(tmp_folder, enc_dir, password=password)
        engine.decrypt_folder(enc_dir, dec_dir, password=password)

        for rel_path, content in original_files.items():
            assert (dec_dir / rel_path).read_bytes() == content

    def test_encrypt_folder_progress_callback(
        self, engine: AESEngine, tmp_folder: Path, tmp_path: Path, password: str
    ) -> None:
        calls: list[tuple[int, int, str]] = []

        def on_progress(current: int, total: int, filename: str) -> None:
            calls.append((current, total, filename))

        enc_dir = tmp_path / "encrypted"
        engine.encrypt_folder(
            tmp_folder, enc_dir, password=password, progress=on_progress
        )

        assert len(calls) > 0
        assert calls[-1][0] == calls[-1][1]  # last call: current == total
