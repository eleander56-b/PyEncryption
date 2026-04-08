"""Tests for the CLI interface."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from pyencryption.cli import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    f = tmp_path / "test.txt"
    f.write_bytes(b"CLI test content for encryption")
    return f


class TestEncryptCommand:
    def test_encrypt_file(self, runner: CliRunner, sample_file: Path) -> None:
        result = runner.invoke(main, ["encrypt", str(sample_file), "-p", "testpass"])
        assert result.exit_code == 0
        assert "Encrypted" in result.output

    def test_encrypt_no_password_prompts(self, runner: CliRunner, sample_file: Path) -> None:
        result = runner.invoke(
            main, ["encrypt", str(sample_file)], input="testpass\ntestpass\n"
        )
        assert result.exit_code == 0


class TestDecryptCommand:
    def test_decrypt_file(self, runner: CliRunner, sample_file: Path) -> None:
        original = sample_file.read_bytes()
        runner.invoke(main, ["encrypt", str(sample_file), "-p", "testpass"])
        enc_file = sample_file.with_suffix(".txt.enc")

        result = runner.invoke(main, ["decrypt", str(enc_file), "-p", "testpass"])
        assert result.exit_code == 0
        assert "Decrypted" in result.output

        dec_file = enc_file.with_suffix("")
        assert dec_file.read_bytes() == original

    def test_wrong_password_error(self, runner: CliRunner, sample_file: Path) -> None:
        runner.invoke(main, ["encrypt", str(sample_file), "-p", "rightpass"])
        enc_file = sample_file.with_suffix(".txt.enc")

        result = runner.invoke(main, ["decrypt", str(enc_file), "-p", "wrongpass"])
        assert result.exit_code != 0
        assert "Wrong password" in result.output


class TestVersionAndHelp:
    def test_version(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "2.0.0" in result.output

    def test_help(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "PyEncryption" in result.output


class TestFolderOperations:
    def test_encrypt_folder_recursive(self, runner: CliRunner, tmp_path: Path) -> None:
        folder = tmp_path / "data"
        folder.mkdir()
        (folder / "a.txt").write_bytes(b"file a")
        (folder / "b.txt").write_bytes(b"file b")

        result = runner.invoke(
            main, ["encrypt", str(folder), "-p", "testpass", "-r"]
        )
        assert result.exit_code == 0
        assert "Done" in result.output
