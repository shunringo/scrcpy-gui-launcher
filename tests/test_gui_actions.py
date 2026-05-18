# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from themes import DARK_STYLE, LIGHT_STYLE
from i18n import get_lang, set_lang
from main_window import MainWindow


def _build_window(monkeypatch):
    monkeypatch.setattr(MainWindow, "_load_settings", lambda self: None)
    monkeypatch.setattr(MainWindow, "_load_presets", lambda self: None)
    monkeypatch.setattr(MainWindow, "_show_onboarding", lambda self: None)
    window = MainWindow()
    window.settings["onboarding_done"] = True
    return window


def test_language_button_switches_labels(qapp, monkeypatch):
    previous_lang = get_lang()
    window = _build_window(monkeypatch)
    monkeypatch.setattr(window, "_save_settings", lambda: None)
    window.show()

    try:
        before = window._lang_btn.text()
        qapp.processEvents()
        window._lang_btn.click()
        qapp.processEvents()

        assert before == "EN"
        assert window.settings["language"] == "en"
        assert window._lang_btn.text() == "JA"
        assert window._shortcuts_btn.text() == "⌨ Shortcuts"
        assert window._theme_btn.text() == "🌙 Dark"
    finally:
        set_lang(previous_lang)


def test_theme_button_toggles_stylesheet(qapp, monkeypatch):
    window = _build_window(monkeypatch)
    window.show()

    original_stylesheet = qapp.styleSheet()
    try:
        QTest.mouseClick(window._theme_btn, Qt.LeftButton)
        qapp.processEvents()
        assert window.settings["dark_mode"] is False
        assert qapp.styleSheet() == LIGHT_STYLE

        QTest.mouseClick(window._theme_btn, Qt.LeftButton)
        qapp.processEvents()
        assert window.settings["dark_mode"] is True
        assert qapp.styleSheet() == DARK_STYLE
    finally:
        qapp.setStyleSheet(original_stylesheet)


def test_refresh_button_calls_refresh(monkeypatch):
    called = {}

    def fake_refresh(self):
        called["refresh"] = True

    monkeypatch.setattr(MainWindow, "_refresh_devices", fake_refresh)
    window = _build_window(monkeypatch)
    window.show()

    QTest.mouseClick(window._refresh_btn, Qt.LeftButton)

    assert called.get("refresh") is True


def test_run_button_calls_run(monkeypatch):
    called = {}

    def fake_run(self):
        called["run"] = True

    monkeypatch.setattr(MainWindow, "_scrcpy_path_valid", lambda self: True)
    monkeypatch.setattr(MainWindow, "_run_scrcpy", fake_run)
    window = _build_window(monkeypatch)
    window.show()

    assert window._run_btn.isEnabled()
    QTest.mouseClick(window._run_btn, Qt.LeftButton)

    assert called.get("run") is True


def test_run_and_stop_visibility(monkeypatch):
    window = _build_window(monkeypatch)
    window.show()

    window._scrcpy = object()
    window._update_run_button()
    assert not window._run_btn.isVisible()
    assert window._stop_btn.isVisible()

    window._scrcpy = None
    window._update_run_button()
    assert window._run_btn.isVisible()
    assert not window._stop_btn.isVisible()
