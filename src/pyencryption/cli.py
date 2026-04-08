"""Command-line interface for PyEncryption."""

from __future__ import annotations

from pathlib import Path

import click

from pyencryption import __version__
from pyencryption.crypto.aes import AESEngine, AESError
from pyencryption.utils import format_duration, format_size, walk_files


@click.group()
@click.version_option(version=__version__, prog_name="pyencrypt")
def main() -> None:
    """PyEncryption - File encryption tool with AES-256-GCM."""


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--password", "-p",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Encryption password.",
)
@click.option(
    "--recursive", "-r",
    is_flag=True,
    help="Encrypt entire folder recursively.",
)
def encrypt(path: Path, password: str, recursive: bool) -> None:
    """Encrypt a file or folder."""
    try:
        eng = AESEngine()
        if recursive or path.is_dir():
            files = list(walk_files(path))
            total_size = sum(f.stat().st_size for f in files)
            click.echo(
                f"Encrypting {len(files)} files ({format_size(total_size)})..."
            )
            with click.progressbar(length=len(files), label="Encrypting") as bar:
                def progress(current: int, total: int, name: str) -> None:
                    bar.update(1)

                result = eng.encrypt_folder(path, password=password, progress=progress)
            click.secho(
                f"Done in {format_duration(result.elapsed_seconds)}. "
                f"Output: {result.ciphertext_path}",
                fg="green",
            )
        else:
            result = eng.encrypt_file(path, password=password)
            click.secho(
                f"Encrypted in {format_duration(result.elapsed_seconds)}: "
                f"{result.ciphertext_path}",
                fg="green",
            )
    except (AESError, FileNotFoundError) as e:
        raise click.ClickException(str(e)) from e


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--password", "-p",
    prompt=True,
    hide_input=True,
    help="Decryption password.",
)
@click.option(
    "--recursive", "-r",
    is_flag=True,
    help="Decrypt entire folder recursively.",
)
def decrypt(path: Path, password: str, recursive: bool) -> None:
    """Decrypt a file or folder."""
    try:
        eng = AESEngine()
        if recursive or path.is_dir():
            files = list(walk_files(path))
            click.echo(f"Decrypting {len(files)} files...")
            with click.progressbar(length=len(files), label="Decrypting") as bar:
                def progress(current: int, total: int, name: str) -> None:
                    bar.update(1)

                result = eng.decrypt_folder(path, password=password, progress=progress)
            click.secho(
                f"Done in {format_duration(result.elapsed_seconds)}. "
                f"Output: {result.plaintext_path}",
                fg="green",
            )
        else:
            result = eng.decrypt_file(path, password=password)
            click.secho(
                f"Decrypted in {format_duration(result.elapsed_seconds)}: "
                f"{result.plaintext_path}",
                fg="green",
            )
    except (AESError, FileNotFoundError) as e:
        raise click.ClickException(str(e)) from e


@main.command()
def gui() -> None:
    """Launch the graphical interface."""
    try:
        from pyencryption.gui import launch_gui

        launch_gui()
    except ImportError as e:
        raise click.ClickException(
            f"GUI dependencies not available: {e}. "
            "Install with: pip install pyencryption[gui]"
        ) from e
