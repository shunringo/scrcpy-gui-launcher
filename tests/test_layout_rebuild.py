# -*- coding: utf-8 -*-

import os

import pytest

pytest.importorskip("PyQt5")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from main_window import MainWindow


def test_language_switch_keeps_window_size(qapp, monkeypatch):
    monkeypatch.setattr(MainWindow, "_load_settings", lambda self: None)
    monkeypatch.setattr(MainWindow, "_load_presets", lambda self: None)
    monkeypatch.setattr(MainWindow, "_show_onboarding", lambda self: None)
    window = MainWindow()
    monkeypatch.setattr(window, "_save_settings", lambda: None)

    window.resize(1080, 760)
    window.device_list = [("ABC123", "device", "Test Device")]
    window._repopulate_devices(window.device_list)
    window._dev_combo.setCurrentIndex(0)
    window.settings["selected_device"] = "ABC123"

    before = window.size()
    before_lang = window._lang_btn.text()
    window._switch_language()
    after = window.size()

    assert after == before
    assert before_lang == "EN"
    assert window._lang_btn.text() == "JA"
