# -*- coding: utf-8 -*-

import pytest

pytest.importorskip("PyQt5")

from main_window import MainWindow


def test_language_switch_keeps_window_size(monkeypatch):
    window = MainWindow()
    monkeypatch.setattr(window, "_save_settings", lambda: None)

    window.resize(1080, 760)
    window._dev_combo.addItem("✅ [USB] Test Device  (ABC123)  [device]", "ABC123")
    window._dev_combo.setCurrentIndex(0)
    window.settings["selected_device"] = "ABC123"

    before = window.size()
    window._switch_language()
    after = window.size()

    assert after == before
