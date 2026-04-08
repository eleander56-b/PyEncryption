"""Minimal tests for the GUI module."""

from __future__ import annotations

import os
import sys

import pytest

pytestmark = pytest.mark.gui


@pytest.mark.skipif(
    os.environ.get("CI") == "true" or sys.platform != "win32",
    reason="GUI tests require a display and Windows",
)
class TestGUI:
    def test_app_initializes(self) -> None:
        from pyencryption.gui import PyEncryptionApp

        app = PyEncryptionApp()
        assert app.root is not None
        assert app.root.title() == "PyEncryption"
        app.root.destroy()

    def test_app_has_expected_widgets(self) -> None:
        from pyencryption.gui import PyEncryptionApp

        app = PyEncryptionApp()
        # Verify key variables exist
        assert app._mode_var.get() == "file"
        assert app._password_var.get() == ""
        app.root.destroy()
