"""Tkinter GUI for PyEncryption."""

from __future__ import annotations

import threading
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from tkinter import filedialog, messagebox

from pyencryption.crypto.aes import AESEngine
from pyencryption.utils import format_duration

_PAD_X = 10
_PAD_Y = 5


class PyEncryptionApp:
    """Main application window for PyEncryption."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("PyEncryption")
        self.root.geometry("500x380")
        self.root.resizable(False, False)

        self._mode_var = tk.StringVar(value="file")
        self._password_var = tk.StringVar()
        self._show_password = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self) -> None:
        # Mode selection
        mode_frame = ttk.LabelFrame(self.root, text="Mode", padding=5)
        mode_frame.pack(fill="x", padx=_PAD_X, pady=_PAD_Y)

        ttk.Radiobutton(
            mode_frame, text="Single File", variable=self._mode_var, value="file"
        ).pack(side="left", padx=10)
        ttk.Radiobutton(
            mode_frame, text="Folder", variable=self._mode_var, value="folder"
        ).pack(side="left", padx=10)

        # Password entry
        pw_frame = ttk.LabelFrame(self.root, text="Password", padding=5)
        pw_frame.pack(fill="x", padx=_PAD_X, pady=_PAD_Y)

        self._pw_entry = ttk.Entry(
            pw_frame, textvariable=self._password_var, show="*", width=40
        )
        self._pw_entry.pack(side="left", padx=5, fill="x", expand=True)

        self._show_btn = ttk.Checkbutton(
            pw_frame,
            text="Show",
            variable=self._show_password,
            command=self._toggle_password,
        )
        self._show_btn.pack(side="right", padx=5)

        # Action buttons
        btn_frame = ttk.Frame(self.root, padding=5)
        btn_frame.pack(fill="x", padx=_PAD_X, pady=_PAD_Y)

        self._encrypt_btn = ttk.Button(
            btn_frame, text="Encrypt", command=self._on_encrypt
        )
        self._encrypt_btn.pack(side="left", padx=10, expand=True, fill="x")

        self._decrypt_btn = ttk.Button(
            btn_frame, text="Decrypt", command=self._on_decrypt
        )
        self._decrypt_btn.pack(side="left", padx=10, expand=True, fill="x")

        # Progress bar
        self._progress = ttk.Progressbar(self.root, mode="determinate")
        self._progress.pack(fill="x", padx=_PAD_X, pady=_PAD_Y)

        # Log output
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=5)
        log_frame.pack(fill="both", expand=True, padx=_PAD_X, pady=_PAD_Y)

        self._log = tk.Text(log_frame, height=8, state="disabled", wrap="word")
        scrollbar = ttk.Scrollbar(
            log_frame, orient="vertical", command=self._log.yview
        )
        self._log.configure(yscrollcommand=scrollbar.set)
        self._log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _toggle_password(self) -> None:
        self._pw_entry.configure(show="" if self._show_password.get() else "*")

    def _log_message(self, message: str) -> None:
        self._log.configure(state="normal")
        self._log.insert("end", message + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _set_buttons_state(self, state: str) -> None:
        self._encrypt_btn.configure(state=state)
        self._decrypt_btn.configure(state=state)

    def _ask_path(self) -> Path | None:
        mode = self._mode_var.get()
        if mode == "folder":
            path = filedialog.askdirectory(title="Select folder")
        else:
            path = filedialog.askopenfilename(title="Select file")
        return Path(path) if path else None

    def _on_encrypt(self) -> None:
        path = self._ask_path()
        if not path:
            return

        password = self._password_var.get()
        if not password:
            messagebox.showerror("Error", "Password is required.")
            return

        self._set_buttons_state("disabled")
        self._progress["value"] = 0
        self._log_message(f"Encrypting: {path}")

        thread = threading.Thread(
            target=self._run_encrypt, args=(path, password), daemon=True
        )
        thread.start()

    def _run_encrypt(self, path: Path, password: str) -> None:
        try:
            eng = AESEngine()
            if path.is_dir():
                def on_progress(current: int, t: int, name: str) -> None:
                    self.root.after(0, self._update_progress, current, t, name)

                result = eng.encrypt_folder(
                    path, password=password, progress=on_progress
                )
            else:
                result = eng.encrypt_file(path, password=password)
            self.root.after(
                0,
                self._log_message,
                f"Done in {format_duration(result.elapsed_seconds)}: "
                f"{result.ciphertext_path}",
            )
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._set_buttons_state, "normal")

    def _on_decrypt(self) -> None:
        path = self._ask_path()
        if not path:
            return

        password = self._password_var.get()
        if not password:
            messagebox.showerror("Error", "Password is required.")
            return

        self._set_buttons_state("disabled")
        self._progress["value"] = 0
        self._log_message(f"Decrypting: {path}")

        thread = threading.Thread(
            target=self._run_decrypt, args=(path, password), daemon=True
        )
        thread.start()

    def _run_decrypt(self, path: Path, password: str) -> None:
        try:
            eng = AESEngine()
            if path.is_dir():
                def on_progress(current: int, t: int, name: str) -> None:
                    self.root.after(0, self._update_progress, current, t, name)

                result = eng.decrypt_folder(
                    path, password=password, progress=on_progress
                )
            else:
                result = eng.decrypt_file(path, password=password)
            self.root.after(
                0,
                self._log_message,
                f"Done in {format_duration(result.elapsed_seconds)}: "
                f"{result.plaintext_path}",
            )
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._set_buttons_state, "normal")

    def _update_progress(self, current: int, total: int, name: str) -> None:
        pct = (current / total * 100) if total > 0 else 0
        self._progress["value"] = pct
        self._log_message(f"  [{current}/{total}] {name}")

    def _show_error(self, message: str) -> None:
        self._log_message(f"ERROR: {message}")
        messagebox.showerror("Error", message)

    def run(self) -> None:
        """Start the GUI event loop."""
        self.root.mainloop()


def launch_gui() -> None:
    """Entry point for the GUI."""
    app = PyEncryptionApp()
    app.run()
