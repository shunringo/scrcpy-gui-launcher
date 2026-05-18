# -*- coding: utf-8 -*-

from i18n import get_lang, set_lang, tr
from dialogs import ShortcutDialog
from main_window import MainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest


def _build_main_window(monkeypatch):
    monkeypatch.setattr(MainWindow, "_load_settings", lambda self: None)
    monkeypatch.setattr(MainWindow, "_load_presets", lambda self: None)
    monkeypatch.setattr(MainWindow, "_show_onboarding", lambda self: None)
    window = MainWindow()
    window.settings["onboarding_done"] = True
    return window


def test_shortcuts_button_opens_dialog(qapp, monkeypatch):
    window = _build_main_window(monkeypatch)
    window.show()

    opened = {}

    def fake_exec(self):
        opened["dialog"] = self
        return 0

    monkeypatch.setattr(ShortcutDialog, "exec_", fake_exec, raising=False)

    QTest.mouseClick(window._shortcuts_btn, Qt.LeftButton)

    assert opened["dialog"].parent() is window


def test_shortcut_dialog_renders_expected_content(qapp):
    previous_lang = get_lang()
    set_lang("ja")
    try:
        dialog = ShortcutDialog()
        dialog.show()
        qapp.processEvents()

        html = dialog._browser.toHtml()
        text = dialog._browser.toPlainText()

        assert dialog.windowTitle() == tr("shortcuts_title")
        assert dialog.minimumWidth() >= 720
        assert dialog.minimumHeight() >= 640
        assert "github.com/Genymobile/scrcpy" in html
        assert "MOD + q" in text
        assert "キーボードショートカット" in text
        assert "マウスショートカット" in text
    finally:
        set_lang(previous_lang)
