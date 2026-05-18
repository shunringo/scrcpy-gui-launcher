# -*- coding: utf-8 -*-
"""オンボーディングダイアログ・プリセットダイアログ"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QMessageBox, QInputDialog, QTextBrowser,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config import APP_NAME, DEFAULT_SETTINGS
from i18n import tr, get_lang
from shortcut_data import SHORTCUT_NOTES, SHORTCUT_SECTIONS, SHORTCUT_SOURCE_URL


class OnboardingDialog(QDialog):
    @staticmethod
    def _steps() -> list:
        return [
            (tr("onboarding_step1_icon"),
             tr("onboarding_step1_title"),
             tr("onboarding_step1_desc")),
            (tr("onboarding_step2_icon"),
             tr("onboarding_step2_title"),
             tr("onboarding_step2_desc")),
            (tr("onboarding_step3_icon"),
             tr("onboarding_step3_title"),
             tr("onboarding_step3_desc")),
        ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("onboarding_title", app=APP_NAME))
        self.setMinimumWidth(480)
        self.setModal(True)
        self.step = 0
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(24, 20, 24, 20)

        dot_row = QHBoxLayout()
        self._dots = []
        for _ in self._steps():
            d = QLabel("●")
            d.setAlignment(Qt.AlignCenter)
            self._dots.append(d)
            dot_row.addWidget(d)
        lay.addLayout(dot_row)

        self._icon = QLabel()
        self._icon.setAlignment(Qt.AlignCenter)
        self._icon.setFont(QFont("Segoe UI Emoji", 30))
        lay.addWidget(self._icon)

        self._title = QLabel()
        self._title.setAlignment(Qt.AlignCenter)
        f = QFont(); f.setPointSize(13); f.setBold(True)
        self._title.setFont(f)
        lay.addWidget(self._title)

        self._desc = QLabel()
        self._desc.setWordWrap(True)
        lay.addWidget(self._desc)
        lay.addStretch()

        btns = QHBoxLayout()
        self._skip = QPushButton(tr("onboarding_skip"))
        self._skip.clicked.connect(self.accept)
        self._prev = QPushButton(tr("onboarding_prev"))
        self._prev.clicked.connect(self._go_prev)
        self._next = QPushButton(tr("onboarding_next"))
        self._next.clicked.connect(self._go_next)
        btns.addWidget(self._skip); btns.addStretch()
        btns.addWidget(self._prev); btns.addWidget(self._next)
        lay.addLayout(btns)

    def _refresh(self):
        steps = self._steps()
        icon, title, desc = steps[self.step]
        self._icon.setText(icon)
        self._title.setText(title)
        self._desc.setText(desc)
        for i, d in enumerate(self._dots):
            if i == self.step:   d.setStyleSheet("color:#4CAF50;font-size:16px;")
            elif i < self.step:  d.setStyleSheet("color:#81C784;font-size:12px;")
            else:                d.setStyleSheet("color:#616161;font-size:12px;")
        self._prev.setEnabled(self.step > 0)
        self._next.setText(
            tr("onboarding_start") if self.step == len(steps) - 1
            else tr("onboarding_next"))

    def _go_prev(self):
        if self.step > 0:
            self.step -= 1
            self._refresh()

    def _go_next(self):
        if self.step < len(self._steps()) - 1:
            self.step += 1
            self._refresh()
        else:
            self.accept()


class ShortcutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("shortcuts_title"))
        self.setMinimumWidth(720)
        self.setMinimumHeight(640)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(12)
        lay.setContentsMargins(20, 18, 20, 18)

        intro = QLabel(tr("shortcuts_intro"))
        intro.setWordWrap(True)
        intro.setTextFormat(Qt.RichText)
        intro.setOpenExternalLinks(True)
        lay.addWidget(intro)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setReadOnly(True)
        browser.setHtml(self._build_html())
        lay.addWidget(browser, 1)

        close_btn = QPushButton(tr("preset_close_btn"))
        close_btn.clicked.connect(self.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        lay.addLayout(btn_row)

    def _t(self, text: dict[str, str]) -> str:
        return text["en"] if get_lang() == "en" else text["ja"]

    def _build_html(self) -> str:
        parts = [
            "<html><head><style>",
            "body { font-family: Segoe UI, sans-serif; font-size: 12px; }",
            "h2 { margin-top: 0; }",
            "table { width: 100%; border-collapse: collapse; margin-bottom: 18px; }",
            "th, td { border-bottom: 1px solid #d0d0d0; padding: 6px 8px; text-align: left; vertical-align: top; }",
            "th { background: rgba(127,127,127,0.12); }",
            "ul { margin-top: 8px; }",
            "</style></head><body>",
            f"<h2>{tr('shortcuts_title')}</h2>",
            f"<p>{self._esc(self._t({'ja': 'scrcpy 公式の shortcuts.md を元にした、キーボードとマウス操作の一覧です。', 'en': 'This list is based on scrcpy\'s official shortcuts.md for keyboard and mouse control.'}))}</p>",
            f"<p><a href=\"{SHORTCUT_SOURCE_URL}\">{SHORTCUT_SOURCE_URL}</a></p>",
        ]

        for section in SHORTCUT_SECTIONS:
            parts.append(f"<h3>{self._esc(self._t(section['title']))}</h3>")
            parts.append("<table>")
            parts.append(
                f"<tr><th>{self._esc(self._t({'ja': '操作', 'en': 'Action'}))}</th>"
                f"<th>{self._esc(self._t({'ja': 'ショートカット', 'en': 'Shortcut'}))}</th></tr>"
            )
            for action, shortcut in section["items"]:
                parts.append(
                    "<tr>"
                    f"<td>{self._esc(self._t(action))}</td>"
                    f"<td><code>{self._esc(shortcut)}</code></td>"
                    "</tr>"
                )
            parts.append("</table>")

        parts.append(f"<h3>{self._esc(self._t({'ja': '補足', 'en': 'Notes'}))}</h3>")
        parts.append("<ul>")
        for note in SHORTCUT_NOTES:
            parts.append(f"<li>{self._esc(self._t(note))}</li>")
        parts.append("</ul>")
        parts.append("</body></html>")
        return "".join(parts)

    @staticmethod
    def _esc(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )


class PresetDialog(QDialog):
    # Keys are stable internal names; display names are not translated
    # so saved presets remain compatible across language switches.
    _DEFAULTS = {
        "開発用・仮想ディスプレイ": {
            "new_display": True, "flex_display": True, "vd_dpi": 160,
            "keep_active": True,
        },
        "録画用・高画質": {
            "video_bit_rate": "20M", "max_fps": 60, "max_size": 1920,
            "record_enabled": True, "record_format": "mp4",
        },
        "Quest3ミラーリング": {
            "max_size": 1920, "max_fps": 72, "video_bit_rate": "20M",
        },
    }

    def __init__(self, parent, presets: dict, current: dict):
        super().__init__(parent)
        self.setWindowTitle(tr("preset_title"))
        self.setMinimumWidth(380)
        self.presets = dict(presets)
        self.current = current
        self.loaded  = None
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(16, 16, 16, 16)

        lay.addWidget(QLabel(tr("preset_saved_label")))
        self._list = QComboBox()
        self._list.addItems(list(self.presets))
        lay.addWidget(self._list)

        row = QHBoxLayout()
        for label, fn in [(tr("preset_load_btn"),   self._load),
                          (tr("preset_save_btn"),   self._save),
                          (tr("preset_delete_btn"), self._delete)]:
            b = QPushButton(label); b.clicked.connect(fn); row.addWidget(b)
        lay.addLayout(row)

        lay.addWidget(QLabel(tr("preset_add_defaults_label")))
        for name in self._DEFAULTS:
            if name not in self.presets:
                b = QPushButton(f"＋ {name}")
                b.setProperty("pname", name)
                b.clicked.connect(self._add_default)
                lay.addWidget(b)

        close = QPushButton(tr("preset_close_btn"))
        close.clicked.connect(self.accept)
        lay.addWidget(close)

    def _load(self):
        name = self._list.currentText()
        if name in self.presets:
            self.loaded = self.presets[name]
            self.accept()

    def _save(self):
        name, ok = QInputDialog.getText(
            self, tr("preset_save_title"), tr("preset_save_name_label"))
        if ok and name.strip():
            self.presets[name.strip()] = dict(self.current)
            if self._list.findText(name.strip()) < 0:
                self._list.addItem(name.strip())

    def _delete(self):
        name = self._list.currentText()
        if name and name in self.presets:
            if QMessageBox.question(
                    self, tr("preset_delete_title"),
                    tr("preset_delete_msg", name=name),
                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                del self.presets[name]
                self._list.removeItem(self._list.currentIndex())

    def _add_default(self):
        name = self.sender().property("pname")
        merged = dict(DEFAULT_SETTINGS)
        merged.update(self._DEFAULTS[name])
        self.presets[name] = merged
        self._list.addItem(name)
        self.sender().setEnabled(False)
