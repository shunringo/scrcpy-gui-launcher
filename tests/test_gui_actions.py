# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from themes import DARK_STYLE, LIGHT_STYLE
from main_window import MainWindow


def _build_window(monkeypatch):
    monkeypatch.setattr(MainWindow, "_load_settings", lambda self: None)
    monkeypatch.setattr(MainWindow, "_load_presets", lambda self: None)
    monkeypatch.setattr(MainWindow, "_show_onboarding", lambda self: None)
    window = MainWindow()
    window.settings["onboarding_done"] = True
    return window


def test_language_button_triggers_switch(qapp, monkeypatch):
    called = {}

    def fake_switch(self):
        called["switch"] = True

    monkeypatch.setattr(MainWindow, "_switch_language", fake_switch)
    window = _build_window(monkeypatch)

    window._lang_btn.click()

    assert called.get("switch") is True


def test_theme_button_toggles_stylesheet(qapp, monkeypatch):
    original_stylesheet = qapp.styleSheet()
    window = _build_window(monkeypatch)
    window.show()

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


def test_refresh_button_calls_refresh(qapp, monkeypatch):
    called = {}

    def fake_refresh(self):
        called["refresh"] = True

    monkeypatch.setattr(MainWindow, "_refresh_devices", fake_refresh)
    window = _build_window(monkeypatch)
    window.show()

    QTest.mouseClick(window._refresh_btn, Qt.LeftButton)

    assert called.get("refresh") is True


def test_run_button_calls_run(qapp, monkeypatch):
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


def test_run_and_stop_visibility(qapp, monkeypatch):
    window = _build_window(monkeypatch)
    window.show()
    qapp.processEvents()

    window._scrcpy = object()
    window._update_run_button()
    qapp.processEvents()
    assert window._run_btn.isHidden()
    assert not window._stop_btn.isHidden()

    window._scrcpy = None
    window._update_run_button()
    qapp.processEvents()
    assert not window._run_btn.isHidden()
    assert window._stop_btn.isHidden()
