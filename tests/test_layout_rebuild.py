# -*- coding: utf-8 -*-

import os

import pytest

pytest.importorskip("PyQt5")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

from main_window import MainWindow


def test_language_switch_keeps_window_size(monkeypatch):
    app = QApplication.instance() or QApplication([])
    assert app is not None

    window = MainWindow()
    monkeypatch.setattr(window, "_save_settings", lambda: None)

    window.resize(1080, 760)
    window.device_list = [("ABC123", "device", "Test Device")]
    window._repopulate_devices(window.device_list)
    window._dev_combo.setCurrentIndex(0)
    window.settings["selected_device"] = "ABC123"

    before = window.size()
    window._switch_language()
    after = window.size()

    assert after == before
