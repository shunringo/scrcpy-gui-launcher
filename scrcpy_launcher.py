#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scrcpy GUI Launcher v1.0
scrcpy v4.0 対応 GUI ランチャー
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QGridLayout, QLabel, QPushButton, QComboBox, QSlider, QLineEdit,
        QSpinBox, QCheckBox, QRadioButton, QTabWidget, QTextEdit,
        QFileDialog, QMessageBox, QGroupBox, QScrollArea, QDialog,
        QInputDialog, QFrame, QColorDialog,
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer, QProcess, QSignalBlocker
    from PyQt5.QtGui import QFont, QColor, QTextCursor
except ImportError:
    print("PyQt5 が見つかりません。")
    print("pip install PyQt5  を実行してからもう一度起動してください。")
    input("Enterキーで終了...")
    sys.exit(1)

# ── パス解決 ────────────────────────────────────────────
if getattr(sys, "frozen", False):
    SCRIPT_DIR = Path(sys.executable).parent.resolve()
else:
    SCRIPT_DIR = Path(__file__).parent.resolve()

# launcher/ サブフォルダ構成の場合、scrcpy 本体は親フォルダにある
SCRCPY_SEARCH_DIRS = [SCRIPT_DIR.parent, SCRIPT_DIR]

SETTINGS_FILE = SCRIPT_DIR / "scrcpy_launcher_settings.json"
PRESETS_FILE  = SCRIPT_DIR / "scrcpy_launcher_presets.json"

APP_NAME    = "scrcpy GUI Launcher"
APP_VERSION = "1.0"
SETTINGS_VERSION = 2

# ── デフォルト設定 ──────────────────────────────────────
DEFAULT_SETTINGS: dict = {
    "_version": SETTINGS_VERSION,
    "scrcpy_path": "",
    "connection_type": "usb",
    "wifi_ip": "192.168.1.",
    "wifi_port": "5555",
    "pair_ip": "",
    "pair_port": "5556",
    "pair_code": "",
    "selected_device": "",
    # 表示
    "max_size": 0,
    "max_fps": 60,
    "video_bit_rate": "8M",
    "fullscreen": False,
    "always_on_top": False,
    "rotation": 0,
    "no_audio": False,
    "keep_active": False,
    "kill_adb_on_close": False,
    "background_color": "",
    # 仮想ディスプレイ
    "new_display": False,
    "flex_display": False,
    "vd_width": 1280,
    "vd_height": 720,
    "vd_dpi": 160,
    "start_app": "",
    "no_vd_destroy_content": False,
    "no_vd_system_decorations": False,
    # カメラ
    "camera_mode": False,
    "camera_facing": "back",
    "camera_zoom": 0,
    "camera_torch": False,
    # 録画
    "record_enabled": False,
    "record_file": "",
    "record_format": "mp4",
    "no_display": False,
    # アプリ
    "dark_mode": True,
    "onboarding_done": False,
}

# ── コマンド生成 ────────────────────────────────────────
def build_args(settings: dict, device_serial: str) -> list:
    """scrcpy.exe に渡す引数リストを返す（実行ファイルパス自体は含まない）"""
    args: list = []
    if device_serial:
        args += ["-s", device_serial]

    # 表示
    if settings.get("max_size", 0) > 0:
        args += ["--max-size", str(settings["max_size"])]
    fps = settings.get("max_fps", 60)
    if fps != 60:
        args += ["--max-fps", str(fps)]
    br = settings.get("video_bit_rate", "8M")
    if br != "8M":
        args += ["--video-bit-rate", br]
    if settings.get("fullscreen"):
        args.append("--fullscreen")
    if settings.get("always_on_top"):
        args.append("--always-on-top")
    rot = settings.get("rotation", 0)
    if rot > 0:
        args += ["--rotation", str(rot)]
    if settings.get("no_audio"):
        args.append("--no-audio")
    if settings.get("keep_active"):
        args.append("--keep-active")
    if settings.get("kill_adb_on_close"):
        args.append("--kill-adb-on-close")
    bg = settings.get("background_color", "")
    if bg:
        args += ["--background-color", f"#{bg}"]

    # 仮想ディスプレイ（カメラモードと排他）
    if settings.get("new_display") and not settings.get("camera_mode"):
        if settings.get("flex_display"):
            dpi = settings.get("vd_dpi", 160)
            args.append(f"--new-display=/{dpi}")
            args.append("--flex-display")
        else:
            w   = settings.get("vd_width", 1280)
            h   = settings.get("vd_height", 720)
            dpi = settings.get("vd_dpi", 160)
            args.append(f"--new-display={w}x{h}/{dpi}")
        if settings.get("no_vd_destroy_content"):
            args.append("--no-vd-destroy-content")
        if settings.get("no_vd_system_decorations"):
            args.append("--no-vd-system-decorations")
        if settings.get("start_app"):
            args += ["--start-app", settings["start_app"]]

    # カメラ
    if settings.get("camera_mode"):
        args.append("--video-source=camera")
        facing = settings.get("camera_facing", "back")
        args.append(f"--camera-facing={facing}")
        zoom = settings.get("camera_zoom", 0)
        if zoom > 0:
            args.append(f"--camera-zoom={zoom}")
        if settings.get("camera_torch"):
            args.append("--camera-torch")

    # 録画
    if settings.get("record_enabled") and settings.get("record_file"):
        args += ["--record", settings["record_file"]]
        fmt = settings.get("record_format", "mp4")
        if fmt != "mp4":
            args += ["--record-format", fmt]
        if settings.get("no_display"):
            args.append("--no-display")

    return args


def build_command_preview(settings: dict, device_serial: str) -> str:
    exe  = Path(settings.get("scrcpy_path", "") or "scrcpy.exe").name
    args = build_args(settings, device_serial)
    parts = [exe] + args
    # Quote args that contain spaces
    quoted = []
    for p in parts:
        quoted.append(f'"{p}"' if " " in p else p)
    return " ".join(quoted)


# ── ADB ワーカー ────────────────────────────────────────
class AdbWorker(QThread):
    result = pyqtSignal(str, bool)  # (output, success)

    def __init__(self, adb_path: str, args: list):
        super().__init__()
        self.adb_path = adb_path
        self.args = args

    def run(self):
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        try:
            r = subprocess.run(
                [self.adb_path] + self.args,
                capture_output=True, text=True, timeout=15,
                creationflags=flags,
            )
            self.result.emit((r.stdout + r.stderr).strip(), r.returncode == 0)
        except Exception as e:
            self.result.emit(str(e), False)


# ── テーマ ──────────────────────────────────────────────
DARK_STYLE = """
QWidget { background-color:#1a1a2e; color:#e0e0e0;
  font-family:"Yu Gothic UI","Noto Sans JP","Meiryo UI",sans-serif; }
QMainWindow, QDialog { background-color:#1a1a2e; }
QGroupBox { border:1px solid #3a3a5c; border-radius:6px; margin-top:8px;
  padding-top:8px; color:#a0a0c0; font-weight:bold; }
QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 4px; }
QPushButton { background-color:#16213e; color:#e0e0e0; border:1px solid #4a4a7a;
  border-radius:5px; padding:5px 12px; min-height:22px; }
QPushButton:hover { background-color:#0f3460; border-color:#4CAF50; }
QPushButton:pressed { background-color:#0a2840; }
QPushButton:disabled { background-color:#2a2a4a; color:#606080; border-color:#3a3a5a; }
QPushButton#runButton { background-color:#1b5e20; color:#fff; border:1px solid #4CAF50;
  font-weight:bold; font-size:13px; padding:8px 22px; }
QPushButton#runButton:hover { background-color:#2e7d32; }
QPushButton#runButton:disabled { background-color:#2a2a4a; border-color:#3a3a5a; }
QPushButton#stopButton { background-color:#7f0000; color:#fff; border:1px solid #ef5350;
  font-weight:bold; font-size:13px; padding:8px 22px; }
QPushButton#stopButton:hover { background-color:#b71c1c; }
QComboBox { background-color:#16213e; color:#e0e0e0; border:1px solid #4a4a7a;
  border-radius:4px; padding:4px 8px; min-height:22px; }
QComboBox::drop-down { border:none; width:18px; }
QComboBox QAbstractItemView { background-color:#16213e; color:#e0e0e0;
  selection-background-color:#0f3460; border:1px solid #4a4a7a; }
QLineEdit, QSpinBox { background-color:#16213e; color:#e0e0e0; border:1px solid #4a4a7a;
  border-radius:4px; padding:4px 8px; min-height:22px; }
QLineEdit:focus, QSpinBox:focus { border-color:#4CAF50; }
QLineEdit:read-only { background-color:#12121e; color:#80ff60; }
QTabWidget::pane { border:1px solid #3a3a5c; border-radius:4px; }
QTabBar::tab { background-color:#16213e; color:#a0a0c0; border:1px solid #3a3a5c;
  padding:6px 14px; border-radius:4px 4px 0 0; }
QTabBar::tab:selected { background-color:#0f3460; color:#4CAF50;
  border-bottom:2px solid #4CAF50; }
QTabBar::tab:hover:!selected { background-color:#1a3050; color:#e0e0e0; }
QSlider::groove:horizontal { height:6px; background:#3a3a5c; border-radius:3px; }
QSlider::handle:horizontal { background:#4CAF50; width:16px; height:16px;
  margin:-5px 0; border-radius:8px; }
QSlider::sub-page:horizontal { background:#4CAF50; border-radius:3px; }
QCheckBox { color:#e0e0e0; spacing:6px; }
QCheckBox::indicator { width:16px; height:16px; border:1px solid #4a4a7a;
  border-radius:3px; background-color:#16213e; }
QCheckBox::indicator:checked { background-color:#4CAF50; border-color:#4CAF50; }
QRadioButton { color:#e0e0e0; spacing:6px; }
QRadioButton::indicator { width:14px; height:14px; border:1px solid #4a4a7a;
  border-radius:7px; background-color:#16213e; }
QRadioButton::indicator:checked { background-color:#4CAF50; border-color:#4CAF50; }
QTextEdit { background-color:#0d0d1a; color:#a0ff80; border:1px solid #3a3a5c;
  border-radius:4px; font-family:"Consolas","Courier New",monospace; font-size:11px; }
QScrollBar:vertical { background:#1a1a2e; width:10px; border-radius:5px; }
QScrollBar::handle:vertical { background:#4a4a7a; border-radius:5px; min-height:20px; }
QFrame[frameShape="4"] { color:#3a3a5c; }
QLabel#headerTitle { color:#4CAF50; font-size:15px; font-weight:bold; }
QLabel#infoLabel { background:#1a3a1a; padding:6px 8px; border-radius:4px; color:#a5d6a7; }
QLabel#warnLabel { background:#3a2a00; padding:6px 8px; border-radius:4px; color:#ffcc80; }
"""

LIGHT_STYLE = """
QWidget { background-color:#f5f5f5; color:#212121;
  font-family:"Yu Gothic UI","Noto Sans JP","Meiryo UI",sans-serif; }
QMainWindow, QDialog { background-color:#f5f5f5; }
QGroupBox { border:1px solid #bdbdbd; border-radius:6px; margin-top:8px;
  padding-top:8px; color:#616161; font-weight:bold; }
QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 4px; }
QPushButton { background-color:#ffffff; color:#212121; border:1px solid #bdbdbd;
  border-radius:5px; padding:5px 12px; min-height:22px; }
QPushButton:hover { background-color:#e8f5e9; border-color:#4CAF50; }
QPushButton:disabled { background-color:#eeeeee; color:#9e9e9e; border-color:#e0e0e0; }
QPushButton#runButton { background-color:#4CAF50; color:#fff; border:1px solid #388E3C;
  font-weight:bold; font-size:13px; padding:8px 22px; }
QPushButton#runButton:hover { background-color:#388E3C; }
QPushButton#runButton:disabled { background-color:#a5d6a7; border-color:#81C784; }
QPushButton#stopButton { background-color:#ef5350; color:#fff; border:1px solid #c62828;
  font-weight:bold; font-size:13px; padding:8px 22px; }
QPushButton#stopButton:hover { background-color:#c62828; }
QComboBox { background-color:#fff; color:#212121; border:1px solid #bdbdbd;
  border-radius:4px; padding:4px 8px; min-height:22px; }
QComboBox QAbstractItemView { background-color:#fff; color:#212121;
  selection-background-color:#e8f5e9; border:1px solid #bdbdbd; }
QLineEdit, QSpinBox { background-color:#fff; color:#212121; border:1px solid #bdbdbd;
  border-radius:4px; padding:4px 8px; min-height:22px; }
QLineEdit:focus, QSpinBox:focus { border-color:#4CAF50; }
QLineEdit:read-only { background-color:#f0f0f0; color:#2e7d32; }
QTabWidget::pane { border:1px solid #bdbdbd; border-radius:4px; }
QTabBar::tab { background-color:#eeeeee; color:#616161; border:1px solid #bdbdbd; padding:6px 14px; }
QTabBar::tab:selected { background-color:#fff; color:#4CAF50; border-bottom:2px solid #4CAF50; }
QSlider::groove:horizontal { height:6px; background:#bdbdbd; border-radius:3px; }
QSlider::handle:horizontal { background:#4CAF50; width:16px; height:16px;
  margin:-5px 0; border-radius:8px; }
QSlider::sub-page:horizontal { background:#4CAF50; border-radius:3px; }
QCheckBox { color:#212121; spacing:6px; }
QCheckBox::indicator { width:16px; height:16px; border:1px solid #bdbdbd;
  border-radius:3px; background-color:#fff; }
QCheckBox::indicator:checked { background-color:#4CAF50; border-color:#4CAF50; }
QRadioButton { color:#212121; spacing:6px; }
QRadioButton::indicator { width:14px; height:14px; border:1px solid #bdbdbd;
  border-radius:7px; background-color:#fff; }
QRadioButton::indicator:checked { background-color:#4CAF50; border-color:#4CAF50; }
QTextEdit { background-color:#fafafa; color:#212121; border:1px solid #bdbdbd;
  border-radius:4px; font-family:"Consolas","Courier New",monospace; font-size:11px; }
QScrollBar:vertical { background:#f5f5f5; width:10px; border-radius:5px; }
QScrollBar::handle:vertical { background:#bdbdbd; border-radius:5px; min-height:20px; }
QLabel#headerTitle { color:#2e7d32; font-size:15px; font-weight:bold; }
QLabel#infoLabel { background:#e8f5e9; padding:6px 8px; border-radius:4px; color:#2e7d32; }
QLabel#warnLabel { background:#fff8e1; padding:6px 8px; border-radius:4px; color:#e65100; }
"""


# ── オンボーディングダイアログ ──────────────────────────
class OnboardingDialog(QDialog):
    STEPS = [
        ("📱", "Step 1: デバイスを接続する",
         "AndroidデバイスをUSBケーブルでPCに接続してください。\n\n"
         "デバイス側で「USBデバッグ」を有効にする必要があります。\n"
         "設定 → 開発者オプション → USBデバッグ をONにしてください。\n\n"
         "※ 開発者オプションが表示されない場合は\n"
         "  設定 → 端末情報 → ビルド番号 を7回タップしてください。"),
        ("⚙️", "Step 2: scrcpy の設定をする",
         "右側の設定タブから各種オプションを設定してください。\n\n"
         "• 表示タブ  ：解像度・FPS・ビットレートなどの表示設定\n"
         "• 仮想画面タブ：仮想ディスプレイの作成（v4.0新機能）\n"
         "• カメラタブ ：カメラ映像のミラーリング（v4.0新機能）\n"
         "• 録画タブ  ：画面録画の設定\n\n"
         "画面下部のコマンドプレビューで生成されるコマンドを確認できます。"),
        ("▶️", "Step 3: scrcpy を実行する",
         "「🔄 デバイスを更新」ボタンでデバイスを検出し、\n"
         "「▶ scrcpy を実行」ボタンをクリックして起動してください。\n\n"
         "よく使う設定は「⚙ プリセット」から名前を付けて保存できます。\n\n"
         "実行ログエリアで scrcpy の出力をリアルタイムに確認できます。"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"ようこそ！ {APP_NAME}")
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
        for _ in self.STEPS:
            d = QLabel("●")
            d.setAlignment(Qt.AlignCenter)
            self._dots.append(d)
            dot_row.addWidget(d)
        lay.addLayout(dot_row)

        self._icon  = QLabel(); self._icon.setAlignment(Qt.AlignCenter)
        self._icon.setFont(QFont("Segoe UI Emoji", 30))
        lay.addWidget(self._icon)

        self._title = QLabel(); self._title.setAlignment(Qt.AlignCenter)
        f = QFont(); f.setPointSize(13); f.setBold(True)
        self._title.setFont(f)
        lay.addWidget(self._title)

        self._desc = QLabel(); self._desc.setWordWrap(True)
        lay.addWidget(self._desc)
        lay.addStretch()

        btns = QHBoxLayout()
        self._skip = QPushButton("スキップ"); self._skip.clicked.connect(self.accept)
        self._prev = QPushButton("◀ 前へ");   self._prev.clicked.connect(self._go_prev)
        self._next = QPushButton("次へ ▶");   self._next.clicked.connect(self._go_next)
        btns.addWidget(self._skip); btns.addStretch()
        btns.addWidget(self._prev); btns.addWidget(self._next)
        lay.addLayout(btns)

    def _refresh(self):
        icon, title, desc = self.STEPS[self.step]
        self._icon.setText(icon); self._title.setText(title); self._desc.setText(desc)
        for i, d in enumerate(self._dots):
            if i == self.step:   d.setStyleSheet("color:#4CAF50;font-size:16px;")
            elif i < self.step:  d.setStyleSheet("color:#81C784;font-size:12px;")
            else:                d.setStyleSheet("color:#616161;font-size:12px;")
        self._prev.setEnabled(self.step > 0)
        self._next.setText("✓ 始める" if self.step == len(self.STEPS)-1 else "次へ ▶")

    def _go_prev(self):
        if self.step > 0: self.step -= 1; self._refresh()

    def _go_next(self):
        if self.step < len(self.STEPS)-1: self.step += 1; self._refresh()
        else: self.accept()


# ── プリセットダイアログ ────────────────────────────────
class PresetDialog(QDialog):
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
        self.setWindowTitle("プリセット管理")
        self.setMinimumWidth(380)
        self.presets = dict(presets)
        self.current = current
        self.loaded  = None
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(10); lay.setContentsMargins(16, 16, 16, 16)

        lay.addWidget(QLabel("保存済みプリセット:"))
        self._list = QComboBox()
        self._list.addItems(list(self.presets))
        lay.addWidget(self._list)

        row = QHBoxLayout()
        for label, fn in [("📂 読み込み", self._load),
                          ("💾 現在の設定を保存", self._save),
                          ("🗑 削除", self._delete)]:
            b = QPushButton(label); b.clicked.connect(fn); row.addWidget(b)
        lay.addLayout(row)

        lay.addWidget(QLabel("デフォルトプリセットを追加:"))
        for name in self._DEFAULTS:
            if name not in self.presets:
                b = QPushButton(f"＋ {name}")
                b.setProperty("pname", name)
                b.clicked.connect(self._add_default)
                lay.addWidget(b)

        close = QPushButton("閉じる"); close.clicked.connect(self.accept)
        lay.addWidget(close)

    def _load(self):
        name = self._list.currentText()
        if name in self.presets:
            self.loaded = self.presets[name]; self.accept()

    def _save(self):
        name, ok = QInputDialog.getText(self, "プリセット保存", "プリセット名:")
        if ok and name.strip():
            self.presets[name.strip()] = dict(self.current)
            if self._list.findText(name.strip()) < 0:
                self._list.addItem(name.strip())

    def _delete(self):
        name = self._list.currentText()
        if name and name in self.presets:
            if QMessageBox.question(self, "削除確認", f'"{name}" を削除しますか？',
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


# ── メインウィンドウ ────────────────────────────────────
class MainWindow(QMainWindow):
    _log_sig = pyqtSignal(str, str)   # (message, level)

    def __init__(self):
        super().__init__()
        self.settings: dict = dict(DEFAULT_SETTINGS)
        self.presets:  dict = {}
        self.device_list: list = []           # [(serial, state), ...]
        self._scrcpy: QProcess | None = None
        self._adb_worker: AdbWorker | None = None
        self._init_done = False

        self._load_settings()
        self._load_presets()
        self._find_scrcpy()

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(960, 680)
        self._build_ui()
        self._apply_theme()
        self._log_sig.connect(self._append_log)
        self._init_done = True
        self._update_command_preview()
        self._validate_scrcpy_path()
        self._update_run_button()

        if not self.settings.get("onboarding_done"):
            QTimer.singleShot(200, self._show_onboarding)

    # ── パス ──────────────────────────────────────────────
    def _find_scrcpy(self):
        if not self.settings.get("scrcpy_path"):
            for d in SCRCPY_SEARCH_DIRS:
                candidate = d / "scrcpy.exe"
                if candidate.exists():
                    self.settings["scrcpy_path"] = str(candidate)
                    break

    def _adb_path(self) -> str:
        base = Path(self.settings.get("scrcpy_path", "") or "")
        candidates = [base.parent / "adb.exe"] + [d / "adb.exe" for d in SCRCPY_SEARCH_DIRS]
        for p in candidates:
            if p.exists():
                return str(p)
        return "adb"

    # ── UI 構築 ────────────────────────────────────────────
    def _build_ui(self):
        root = QWidget(); self.setCentralWidget(root)
        vlay = QVBoxLayout(root)
        vlay.setSpacing(0); vlay.setContentsMargins(0, 0, 0, 0)

        vlay.addWidget(self._mk_header())

        body = QWidget()
        hlay = QHBoxLayout(body)
        hlay.setSpacing(0); hlay.setContentsMargins(0, 0, 0, 0)

        left = self._mk_left_panel()
        left.setMinimumWidth(220); left.setMaximumWidth(255)
        hlay.addWidget(left)
        sep = QFrame(); sep.setFrameShape(QFrame.VLine); sep.setFrameShadow(QFrame.Sunken)
        hlay.addWidget(sep)
        hlay.addWidget(self._mk_right_panel(), 1)

        vlay.addWidget(body, 1)
        vlay.addWidget(self._mk_footer())
        vlay.addWidget(self._mk_log_area())

    # ── ヘッダー ───────────────────────────────────────────
    def _mk_header(self) -> QWidget:
        w = QWidget(); w.setFixedHeight(52)
        lay = QHBoxLayout(w); lay.setContentsMargins(14, 6, 14, 6)
        lbl = QLabel(f"🎛  {APP_NAME}  v{APP_VERSION}")
        lbl.setObjectName("headerTitle")
        lay.addWidget(lbl); lay.addStretch()

        self._theme_btn = QPushButton()
        self._theme_btn.setCheckable(True)
        self._theme_btn.setChecked(self.settings.get("dark_mode", True))
        self._theme_btn.clicked.connect(self._toggle_theme)
        self._sync_theme_btn_text()
        lay.addWidget(self._theme_btn)

        help_btn = QPushButton("？ ヘルプ")
        help_btn.clicked.connect(self._show_onboarding)
        lay.addWidget(help_btn)
        return w

    # ── 左パネル ───────────────────────────────────────────
    def _mk_left_panel(self) -> QWidget:
        panel = QWidget()
        lay = QVBoxLayout(panel); lay.setContentsMargins(10, 10, 6, 10); lay.setSpacing(10)

        # デバイス
        dg = QGroupBox("📱 デバイス")
        dl = QVBoxLayout(dg); dl.setSpacing(5)

        self._dev_combo = QComboBox()
        self._dev_combo.setPlaceholderText("デバイスを選択...")
        self._dev_combo.currentIndexChanged.connect(self._on_device_changed)
        dl.addWidget(self._dev_combo)

        self._dev_status = QLabel("デバイスが見つかりません")
        self._dev_status.setWordWrap(True)
        self._dev_status.setStyleSheet("color:#ff9800;font-size:11px;")
        dl.addWidget(self._dev_status)

        ref_btn = QPushButton("🔄 デバイスを更新")
        ref_btn.clicked.connect(self._refresh_devices)
        dl.addWidget(ref_btn)
        lay.addWidget(dg)

        # 接続方式
        cg = QGroupBox("🔌 接続方式")
        cl = QVBoxLayout(cg); cl.setSpacing(5)

        self._usb_rb  = QRadioButton("USB 接続")
        self._wifi_rb = QRadioButton("Wi-Fi 接続")
        is_wifi = self.settings.get("connection_type") == "wifi"
        self._usb_rb.setChecked(not is_wifi); self._wifi_rb.setChecked(is_wifi)
        self._usb_rb.toggled.connect(self._on_conn_type_changed)
        cl.addWidget(self._usb_rb); cl.addWidget(self._wifi_rb)

        self._wifi_box = QWidget()
        wl = QVBoxLayout(self._wifi_box); wl.setContentsMargins(0, 4, 0, 0); wl.setSpacing(4)
        wl.addWidget(QLabel("IP アドレス:"))
        self._wifi_ip   = QLineEdit(self.settings.get("wifi_ip", "192.168.1."))
        self._wifi_ip.setPlaceholderText("192.168.1.xxx"); wl.addWidget(self._wifi_ip)
        wl.addWidget(QLabel("ポート:"))
        self._wifi_port = QLineEdit(self.settings.get("wifi_port", "5555")); wl.addWidget(self._wifi_port)
        conn_btn = QPushButton("🔗 接続"); conn_btn.clicked.connect(self._wifi_connect)
        wl.addWidget(conn_btn)

        pair_g = QGroupBox("ペアリング (Android 11+)")
        pl = QVBoxLayout(pair_g); pl.setSpacing(4)
        pl.addWidget(QLabel("ペア IP : ポート:"))
        pr = QHBoxLayout()
        self._pair_ip   = QLineEdit(self.settings.get("pair_ip", ""))
        self._pair_ip.setPlaceholderText("192.168.1.x")
        self._pair_port = QLineEdit(self.settings.get("pair_port", "5556"))
        self._pair_port.setMaximumWidth(55)
        pr.addWidget(self._pair_ip); pr.addWidget(QLabel(":")); pr.addWidget(self._pair_port)
        pl.addLayout(pr)
        pl.addWidget(QLabel("ペアコード:"))
        self._pair_code = QLineEdit(self.settings.get("pair_code", ""))
        self._pair_code.setPlaceholderText("123456"); pl.addWidget(self._pair_code)
        pb = QPushButton("🔑 ペアリング"); pb.clicked.connect(self._wifi_pair)
        pl.addWidget(pb)
        wl.addWidget(pair_g)

        cl.addWidget(self._wifi_box)
        self._wifi_box.setVisible(is_wifi)
        lay.addWidget(cg)

        # パス設定
        pg = QGroupBox("📁 scrcpy パス")
        pgl = QVBoxLayout(pg); pgl.setSpacing(4)
        self._path_edit = QLineEdit(self.settings.get("scrcpy_path", ""))
        self._path_edit.setPlaceholderText("scrcpy.exe のパス")
        self._path_edit.textChanged.connect(self._on_path_changed)
        pgl.addWidget(self._path_edit)
        br = QPushButton("📂 参照..."); br.clicked.connect(self._browse_scrcpy)
        pgl.addWidget(br)
        self._path_status = QLabel()
        self._path_status.setWordWrap(True)
        self._path_status.setStyleSheet("font-size:11px;")
        pgl.addWidget(self._path_status)
        lay.addWidget(pg)

        lay.addStretch()
        return panel

    # ── 右パネル ───────────────────────────────────────────
    def _mk_right_panel(self) -> QWidget:
        panel = QWidget()
        lay = QVBoxLayout(panel); lay.setContentsMargins(6, 10, 10, 6); lay.setSpacing(8)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._mk_display_tab(),  "🖥 表示")
        self._tabs.addTab(self._mk_vd_tab(),        "📺 仮想画面")
        self._tabs.addTab(self._mk_camera_tab(),    "📷 カメラ")
        self._tabs.addTab(self._mk_record_tab(),    "⏺ 録画")
        lay.addWidget(self._tabs, 1)

        cmd_g = QGroupBox("💻 コマンドプレビュー")
        cmd_l = QHBoxLayout(cmd_g)
        self._cmd_preview = QLineEdit(); self._cmd_preview.setReadOnly(True)
        self._cmd_preview.setFont(QFont("Consolas", 10))
        copy_btn = QPushButton("📋 コピー"); copy_btn.setMaximumWidth(78)
        copy_btn.clicked.connect(self._copy_command)
        cmd_l.addWidget(self._cmd_preview); cmd_l.addWidget(copy_btn)
        lay.addWidget(cmd_g)
        return panel

    # ── 表示タブ ───────────────────────────────────────────
    def _mk_display_tab(self) -> QWidget:
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        w = QWidget(); lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(8, 8, 8, 8)

        rg = QGroupBox("解像度・フレームレート・ビットレート")
        gl = QGridLayout(rg); gl.setColumnStretch(1, 1)

        gl.addWidget(QLabel("最大解像度 (0=制限なし):"), 0, 0)
        self._max_size = QSpinBox(); self._max_size.setRange(0, 7680); self._max_size.setSingleStep(120)
        self._max_size.setValue(self.settings.get("max_size", 0))
        self._max_size.setSuffix(" px"); self._max_size.setSpecialValueText("制限なし")
        self._max_size.valueChanged.connect(self._changed)
        gl.addWidget(self._max_size, 0, 1)

        gl.addWidget(QLabel("最大 FPS:"), 1, 0)
        fps_row = QWidget(); frl = QHBoxLayout(fps_row); frl.setContentsMargins(0,0,0,0)
        self._fps_sl  = QSlider(Qt.Horizontal); self._fps_sl.setRange(1, 120)
        self._fps_sl.setValue(self.settings.get("max_fps", 60))
        self._fps_lbl = QLabel(f"{self.settings.get('max_fps', 60)} fps")
        self._fps_lbl.setMinimumWidth(48)
        self._fps_sl.valueChanged.connect(lambda v: (
            self._fps_lbl.setText(f"{v} fps"), self._changed()))
        frl.addWidget(self._fps_sl); frl.addWidget(self._fps_lbl)
        gl.addWidget(fps_row, 1, 1)

        gl.addWidget(QLabel("ビットレート:"), 2, 0)
        self._bitrate = QComboBox()
        self._bitrate.addItems(["1M","2M","4M","8M","16M","20M","32M"])
        idx = self._bitrate.findText(self.settings.get("video_bit_rate", "8M"))
        if idx >= 0: self._bitrate.setCurrentIndex(idx)
        self._bitrate.currentTextChanged.connect(self._changed)
        gl.addWidget(self._bitrate, 2, 1)
        lay.addWidget(rg)

        dg = QGroupBox("表示オプション")
        dgl = QGridLayout(dg)
        self._fullscreen = QCheckBox("フルスクリーン起動 (--fullscreen)")
        self._fullscreen.setChecked(self.settings.get("fullscreen", False))
        self._fullscreen.stateChanged.connect(self._changed)
        dgl.addWidget(self._fullscreen, 0, 0)

        self._always_top = QCheckBox("常に最前面 (--always-on-top)")
        self._always_top.setChecked(self.settings.get("always_on_top", False))
        self._always_top.stateChanged.connect(self._changed)
        dgl.addWidget(self._always_top, 0, 1)

        dgl.addWidget(QLabel("画面回転:"), 1, 0)
        self._rotation = QComboBox()
        self._rotation.addItems(["0° (変更なし)", "90°", "180°", "270°"])
        self._rotation.setCurrentIndex(self.settings.get("rotation", 0))
        self._rotation.currentIndexChanged.connect(self._changed)
        dgl.addWidget(self._rotation, 1, 1)

        dgl.addWidget(QLabel("背景色 (--background-color):"), 2, 0)
        bg_row = QWidget(); brl = QHBoxLayout(bg_row); brl.setContentsMargins(0,0,0,0)
        self._bg_btn = QPushButton(); self._bg_btn.setFixedWidth(56)
        self._bg_btn.clicked.connect(self._pick_bg)
        clr_btn = QPushButton("クリア"); clr_btn.setMaximumWidth(56)
        clr_btn.clicked.connect(self._clear_bg)
        brl.addWidget(self._bg_btn); brl.addWidget(clr_btn); brl.addStretch()
        dgl.addWidget(bg_row, 2, 1)
        self._refresh_bg_btn(self.settings.get("background_color", ""))
        lay.addWidget(dg)

        og = QGroupBox("動作オプション")
        ogl = QGridLayout(og)
        self._no_audio   = QCheckBox("音声なし (--no-audio)")
        self._keep_alive = QCheckBox("スリープ防止 (--keep-active)")
        self._kill_adb   = QCheckBox("終了時 ADB 停止 (--kill-adb-on-close)")
        self._no_audio.setChecked(self.settings.get("no_audio", False))
        self._keep_alive.setChecked(self.settings.get("keep_active", False))
        self._kill_adb.setChecked(self.settings.get("kill_adb_on_close", False))
        for cb in (self._no_audio, self._keep_alive, self._kill_adb):
            cb.stateChanged.connect(self._changed)
        ogl.addWidget(self._no_audio, 0, 0); ogl.addWidget(self._keep_alive, 0, 1)
        ogl.addWidget(self._kill_adb, 1, 0, 1, 2)
        lay.addWidget(og)

        lay.addStretch()
        scroll.setWidget(w); return scroll

    # ── 仮想画面タブ ───────────────────────────────────────
    def _mk_vd_tab(self) -> QWidget:
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        w = QWidget(); lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(8, 8, 8, 8)

        info = QLabel("ℹ️  カメラモードが有効な場合、仮想ディスプレイは無効になります。")
        info.setObjectName("infoLabel"); info.setWordWrap(True)
        lay.addWidget(info)

        self._new_disp = QCheckBox("仮想ディスプレイを有効にする (--new-display)")
        self._new_disp.setChecked(self.settings.get("new_display", False))
        self._new_disp.stateChanged.connect(self._on_new_disp_changed)
        lay.addWidget(self._new_disp)

        self._vd_box = QWidget()
        vbl = QVBoxLayout(self._vd_box); vbl.setContentsMargins(16, 0, 0, 0); vbl.setSpacing(8)

        self._flex_disp = QCheckBox("フレックスディスプレイ (--flex-display / -x)  ※ウィンドウサイズに追従")
        self._flex_disp.setChecked(self.settings.get("flex_display", False))
        self._flex_disp.stateChanged.connect(self._on_flex_changed)
        vbl.addWidget(self._flex_disp)

        self._vd_res_row = QWidget()
        rrl = QHBoxLayout(self._vd_res_row); rrl.setContentsMargins(0,0,0,0)
        rrl.addWidget(QLabel("解像度 (W × H):"))
        self._vd_w = QSpinBox(); self._vd_w.setRange(1, 7680); self._vd_w.setValue(self.settings.get("vd_width", 1280))
        self._vd_h = QSpinBox(); self._vd_h.setRange(1, 7680); self._vd_h.setValue(self.settings.get("vd_height", 720))
        self._vd_w.valueChanged.connect(self._changed); self._vd_h.valueChanged.connect(self._changed)
        rrl.addWidget(self._vd_w); rrl.addWidget(QLabel(" × ")); rrl.addWidget(self._vd_h); rrl.addStretch()
        vbl.addWidget(self._vd_res_row)

        dpi_row = QHBoxLayout()
        dpi_row.addWidget(QLabel("DPI:"))
        self._vd_dpi = QSpinBox(); self._vd_dpi.setRange(60, 640); self._vd_dpi.setValue(self.settings.get("vd_dpi", 160))
        self._vd_dpi.valueChanged.connect(self._changed)
        dpi_row.addWidget(self._vd_dpi); dpi_row.addStretch()
        vbl.addLayout(dpi_row)

        app_row = QHBoxLayout()
        app_row.addWidget(QLabel("起動アプリ (--start-app):"))
        self._start_app = QLineEdit(self.settings.get("start_app", ""))
        self._start_app.setPlaceholderText("例: com.android.settings")
        self._start_app.textChanged.connect(self._changed)
        app_row.addWidget(self._start_app)
        vbl.addLayout(app_row)

        self._no_vd_dest = QCheckBox("終了時コンテンツ保持 (--no-vd-destroy-content)")
        self._no_vd_decor = QCheckBox("システムデコレーション非表示 (--no-vd-system-decorations)")
        self._no_vd_dest.setChecked(self.settings.get("no_vd_destroy_content", False))
        self._no_vd_decor.setChecked(self.settings.get("no_vd_system_decorations", False))
        self._no_vd_dest.stateChanged.connect(self._changed)
        self._no_vd_decor.stateChanged.connect(self._changed)
        vbl.addWidget(self._no_vd_dest); vbl.addWidget(self._no_vd_decor)

        lay.addWidget(self._vd_box)
        self._vd_box.setEnabled(self.settings.get("new_display", False))
        self._vd_res_row.setVisible(not self.settings.get("flex_display", False))

        lay.addStretch(); scroll.setWidget(w); return scroll

    # ── カメラタブ ─────────────────────────────────────────
    def _mk_camera_tab(self) -> QWidget:
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        w = QWidget(); lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(8, 8, 8, 8)

        info = QLabel("ℹ️  カメラモード ON 時は通常のスクリーンミラーリングではなくカメラ映像を表示します。\n"
                       "カメラモード ON 時、仮想ディスプレイ設定は無効になります。")
        info.setObjectName("infoLabel"); info.setWordWrap(True)
        lay.addWidget(info)

        self._cam_mode = QCheckBox("カメラミラーリングを有効にする (--video-source=camera)")
        self._cam_mode.setChecked(self.settings.get("camera_mode", False))
        self._cam_mode.stateChanged.connect(self._on_camera_mode_changed)
        lay.addWidget(self._cam_mode)

        self._cam_box = QWidget()
        cbl = QVBoxLayout(self._cam_box); cbl.setContentsMargins(16, 0, 0, 0); cbl.setSpacing(8)

        f_row = QHBoxLayout()
        f_row.addWidget(QLabel("カメラ選択 (--camera-facing):"))
        self._cam_facing = QComboBox()
        self._cam_facing.addItems(["リア (back)", "フロント (front)"])
        self._cam_facing.setCurrentIndex(0 if self.settings.get("camera_facing","back") == "back" else 1)
        self._cam_facing.currentIndexChanged.connect(self._changed)
        f_row.addWidget(self._cam_facing); f_row.addStretch()
        cbl.addLayout(f_row)

        z_row = QHBoxLayout()
        z_row.addWidget(QLabel("ズーム (--camera-zoom):"))
        self._cam_zoom = QSlider(Qt.Horizontal); self._cam_zoom.setRange(0, 100)
        self._cam_zoom.setValue(self.settings.get("camera_zoom", 0))
        self._cam_zlbl = QLabel(f"{self.settings.get('camera_zoom', 0)}%"); self._cam_zlbl.setMinimumWidth(36)
        self._cam_zoom.valueChanged.connect(lambda v: (
            self._cam_zlbl.setText(f"{v}%"), self._changed()))
        z_row.addWidget(self._cam_zoom); z_row.addWidget(self._cam_zlbl)
        cbl.addLayout(z_row)

        self._cam_torch = QCheckBox("トーチ（ライト）ON (--camera-torch)")
        self._cam_torch.setChecked(self.settings.get("camera_torch", False))
        self._cam_torch.stateChanged.connect(self._changed)
        cbl.addWidget(self._cam_torch)

        lay.addWidget(self._cam_box)
        self._cam_box.setEnabled(self.settings.get("camera_mode", False))
        lay.addStretch(); scroll.setWidget(w); return scroll

    # ── 録画タブ ───────────────────────────────────────────
    def _mk_record_tab(self) -> QWidget:
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        w = QWidget(); lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(8, 8, 8, 8)

        self._rec_cb = QCheckBox("録画を有効にする (--record)")
        self._rec_cb.setChecked(self.settings.get("record_enabled", False))
        self._rec_cb.stateChanged.connect(self._on_record_changed)
        lay.addWidget(self._rec_cb)

        self._rec_box = QWidget()
        rbl = QVBoxLayout(self._rec_box); rbl.setContentsMargins(16, 0, 0, 0); rbl.setSpacing(8)

        fp_row = QHBoxLayout()
        fp_row.addWidget(QLabel("出力ファイル:"))
        self._rec_file = QLineEdit(self.settings.get("record_file", ""))
        self._rec_file.setPlaceholderText("録画ファイルのパス")
        self._rec_file.textChanged.connect(self._changed)
        br = QPushButton("📂"); br.setMaximumWidth(34); br.clicked.connect(self._browse_record)
        fp_row.addWidget(self._rec_file); fp_row.addWidget(br)
        rbl.addLayout(fp_row)

        df_btn = QPushButton("📅 デフォルトファイル名を使用"); df_btn.clicked.connect(self._use_default_rec_name)
        rbl.addWidget(df_btn)

        fmt_row = QHBoxLayout()
        fmt_row.addWidget(QLabel("フォーマット:"))
        self._rec_fmt = QComboBox(); self._rec_fmt.addItems(["mp4", "mkv", "h264", "opus"])
        idx = self._rec_fmt.findText(self.settings.get("record_format", "mp4"))
        if idx >= 0: self._rec_fmt.setCurrentIndex(idx)
        self._rec_fmt.currentTextChanged.connect(self._changed)
        fmt_row.addWidget(self._rec_fmt); fmt_row.addStretch()
        rbl.addLayout(fmt_row)

        self._no_disp = QCheckBox("録画中ミラーリング非表示 (--no-display)")
        self._no_disp.setChecked(self.settings.get("no_display", False))
        self._no_disp.stateChanged.connect(self._changed)
        rbl.addWidget(self._no_disp)

        lay.addWidget(self._rec_box)
        self._rec_box.setEnabled(self.settings.get("record_enabled", False))
        lay.addStretch(); scroll.setWidget(w); return scroll

    # ── フッター ───────────────────────────────────────────
    def _mk_footer(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w); lay.setContentsMargins(12, 8, 12, 8)

        self._run_btn = QPushButton("▶  scrcpy を実行")
        self._run_btn.setObjectName("runButton"); self._run_btn.setMinimumHeight(42)
        self._run_btn.clicked.connect(self._run_scrcpy)

        self._stop_btn = QPushButton("⏹  停止")
        self._stop_btn.setObjectName("stopButton"); self._stop_btn.setMinimumHeight(42)
        self._stop_btn.clicked.connect(self._stop_scrcpy)
        self._stop_btn.setVisible(False)

        preset_btn = QPushButton("⚙  プリセット"); preset_btn.setMinimumHeight(42)
        preset_btn.clicked.connect(self._open_presets)

        lay.addWidget(self._run_btn); lay.addWidget(self._stop_btn)
        lay.addStretch(); lay.addWidget(preset_btn)
        return w

    # ── ログエリア ─────────────────────────────────────────
    def _mk_log_area(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w); lay.setContentsMargins(8, 0, 8, 8); lay.setSpacing(3)

        hdr = QHBoxLayout()
        lbl = QLabel("📋 実行ログ"); lbl.setStyleSheet("font-weight:bold;")
        hdr.addWidget(lbl); hdr.addStretch()
        for text, fn in [("🗑 クリア", self._clear_log), ("📋 コピー", self._copy_log)]:
            b = QPushButton(text); b.setMaximumWidth(70); b.clicked.connect(fn); hdr.addWidget(b)
        lay.addLayout(hdr)

        self._log = QTextEdit(); self._log.setReadOnly(True)
        self._log.setMaximumHeight(150); self._log.setMinimumHeight(90)
        lay.addWidget(self._log)
        return w

    # ── 設定収集 ────────────────────────────────────────────
    def _collect(self) -> dict:
        """UI の値を self.settings に収集して返す"""
        if not self._init_done:
            return self.settings
        s = self.settings
        s["max_size"]      = self._max_size.value()
        s["max_fps"]       = self._fps_sl.value()
        s["video_bit_rate"] = self._bitrate.currentText()
        s["fullscreen"]    = self._fullscreen.isChecked()
        s["always_on_top"] = self._always_top.isChecked()
        s["rotation"]      = self._rotation.currentIndex()
        s["no_audio"]      = self._no_audio.isChecked()
        s["keep_active"]   = self._keep_alive.isChecked()
        s["kill_adb_on_close"] = self._kill_adb.isChecked()
        s["new_display"]   = self._new_disp.isChecked()
        s["flex_display"]  = self._flex_disp.isChecked()
        s["vd_width"]      = self._vd_w.value()
        s["vd_height"]     = self._vd_h.value()
        s["vd_dpi"]        = self._vd_dpi.value()
        s["start_app"]     = self._start_app.text()
        s["no_vd_destroy_content"]   = self._no_vd_dest.isChecked()
        s["no_vd_system_decorations"] = self._no_vd_decor.isChecked()
        s["camera_mode"]   = self._cam_mode.isChecked()
        s["camera_facing"] = "back" if self._cam_facing.currentIndex() == 0 else "front"
        s["camera_zoom"]   = self._cam_zoom.value()
        s["camera_torch"]  = self._cam_torch.isChecked()
        s["record_enabled"] = self._rec_cb.isChecked()
        s["record_file"]   = self._rec_file.text()
        s["record_format"] = self._rec_fmt.currentText()
        s["no_display"]    = self._no_disp.isChecked()
        s["wifi_ip"]       = self._wifi_ip.text()
        s["wifi_port"]     = self._wifi_port.text()
        s["pair_ip"]       = self._pair_ip.text()
        s["pair_port"]     = self._pair_port.text()
        s["pair_code"]     = self._pair_code.text()
        return s

    def _apply_to_ui(self):
        """self.settings を UI に反映する（シグナルをブロック）"""
        s = self.settings
        blockers = []
        widgets = [
            self._max_size, self._fps_sl, self._bitrate, self._fullscreen, self._always_top,
            self._rotation, self._no_audio, self._keep_alive, self._kill_adb,
            self._new_disp, self._flex_disp, self._vd_w, self._vd_h, self._vd_dpi,
            self._start_app, self._no_vd_dest, self._no_vd_decor,
            self._cam_mode, self._cam_facing, self._cam_zoom, self._cam_torch,
            self._rec_cb, self._rec_file, self._rec_fmt, self._no_disp,
            self._wifi_ip, self._wifi_port, self._pair_ip, self._pair_port, self._pair_code,
        ]
        for w in widgets:
            blockers.append(QSignalBlocker(w))

        self._max_size.setValue(s.get("max_size", 0))
        self._fps_sl.setValue(s.get("max_fps", 60))
        self._fps_lbl.setText(f"{s.get('max_fps', 60)} fps")
        idx = self._bitrate.findText(s.get("video_bit_rate", "8M"))
        if idx >= 0: self._bitrate.setCurrentIndex(idx)
        self._fullscreen.setChecked(s.get("fullscreen", False))
        self._always_top.setChecked(s.get("always_on_top", False))
        self._rotation.setCurrentIndex(s.get("rotation", 0))
        self._no_audio.setChecked(s.get("no_audio", False))
        self._keep_alive.setChecked(s.get("keep_active", False))
        self._kill_adb.setChecked(s.get("kill_adb_on_close", False))
        self._refresh_bg_btn(s.get("background_color", ""))

        self._new_disp.setChecked(s.get("new_display", False))
        self._flex_disp.setChecked(s.get("flex_display", False))
        self._vd_box.setEnabled(s.get("new_display", False))
        self._vd_res_row.setVisible(not s.get("flex_display", False))
        self._vd_w.setValue(s.get("vd_width", 1280))
        self._vd_h.setValue(s.get("vd_height", 720))
        self._vd_dpi.setValue(s.get("vd_dpi", 160))
        self._start_app.setText(s.get("start_app", ""))
        self._no_vd_dest.setChecked(s.get("no_vd_destroy_content", False))
        self._no_vd_decor.setChecked(s.get("no_vd_system_decorations", False))

        self._cam_mode.setChecked(s.get("camera_mode", False))
        self._cam_box.setEnabled(s.get("camera_mode", False))
        self._cam_facing.setCurrentIndex(0 if s.get("camera_facing", "back") == "back" else 1)
        self._cam_zoom.setValue(s.get("camera_zoom", 0))
        self._cam_zlbl.setText(f"{s.get('camera_zoom', 0)}%")
        self._cam_torch.setChecked(s.get("camera_torch", False))

        self._rec_cb.setChecked(s.get("record_enabled", False))
        self._rec_box.setEnabled(s.get("record_enabled", False))
        self._rec_file.setText(s.get("record_file", ""))
        idx = self._rec_fmt.findText(s.get("record_format", "mp4"))
        if idx >= 0: self._rec_fmt.setCurrentIndex(idx)
        self._no_disp.setChecked(s.get("no_display", False))

        is_wifi = s.get("connection_type", "usb") == "wifi"
        self._usb_rb.setChecked(not is_wifi); self._wifi_rb.setChecked(is_wifi)
        self._wifi_box.setVisible(is_wifi)
        self._wifi_ip.setText(s.get("wifi_ip", "192.168.1."))
        self._wifi_port.setText(s.get("wifi_port", "5555"))
        self._pair_ip.setText(s.get("pair_ip", ""))
        self._pair_port.setText(s.get("pair_port", "5556"))
        self._pair_code.setText(s.get("pair_code", ""))
        self._path_edit.setText(s.get("scrcpy_path", ""))

        del blockers  # QSignalBlocker destructor re-enables signals

    # ── イベントハンドラ ───────────────────────────────────
    def _changed(self, *_):
        if not self._init_done: return
        self._collect()
        self._update_command_preview()

    def _on_device_changed(self, idx):
        serial = self._dev_combo.itemData(idx)
        self.settings["selected_device"] = serial or ""
        self._update_run_button()
        self._update_command_preview()

    def _on_conn_type_changed(self):
        is_wifi = self._wifi_rb.isChecked()
        self.settings["connection_type"] = "wifi" if is_wifi else "usb"
        self._wifi_box.setVisible(is_wifi)

    def _on_new_disp_changed(self):
        enabled = self._new_disp.isChecked()
        self._vd_box.setEnabled(enabled)
        self._changed()

    def _on_flex_changed(self):
        self._vd_res_row.setVisible(not self._flex_disp.isChecked())
        self._changed()

    def _on_camera_mode_changed(self):
        enabled = self._cam_mode.isChecked()
        self._cam_box.setEnabled(enabled)
        self._changed()

    def _on_record_changed(self):
        enabled = self._rec_cb.isChecked()
        self._rec_box.setEnabled(enabled)
        if enabled and not self._rec_file.text():
            self._use_default_rec_name()
        self._changed()

    def _on_path_changed(self, text):
        self.settings["scrcpy_path"] = text
        self._validate_scrcpy_path()
        self._update_command_preview()

    # ── UI ヘルパー ────────────────────────────────────────
    def _current_device(self) -> str:
        serial = self._dev_combo.currentData()
        if not serial and len(self.device_list) == 1:
            return self.device_list[0][0]
        return serial or ""

    def _update_command_preview(self):
        if not self._init_done: return
        self._cmd_preview.setText(
            build_command_preview(self.settings, self._current_device()))

    def _update_run_button(self):
        running = self._scrcpy is not None
        path_ok = self._scrcpy_path_valid()
        self._run_btn.setEnabled(path_ok and not running)
        self._run_btn.setVisible(not running)
        self._stop_btn.setVisible(running)

    def _scrcpy_path_valid(self) -> bool:
        p = self.settings.get("scrcpy_path", "")
        return bool(p) and Path(p).exists()

    def _validate_scrcpy_path(self):
        if self._scrcpy_path_valid():
            self._path_status.setText("✅ scrcpy.exe を確認しました")
            self._path_status.setStyleSheet("color:#4CAF50;font-size:11px;")
        else:
            self._path_status.setText("❌ scrcpy.exe が見つかりません")
            self._path_status.setStyleSheet("color:#ef5350;font-size:11px;")
        self._update_run_button()

    def _refresh_bg_btn(self, color: str):
        self.settings["background_color"] = color
        if color:
            self._bg_btn.setStyleSheet(f"background-color:#{color};border:1px solid #888;")
            self._bg_btn.setText(f"#{color}")
        else:
            self._bg_btn.setStyleSheet("")
            self._bg_btn.setText("選択")

    # ── デバイス管理 ────────────────────────────────────────
    def _refresh_devices(self):
        self._dev_status.setText("🔄 検索中...")
        self._dev_status.setStyleSheet("color:#64b5f6;font-size:11px;")
        worker = AdbWorker(self._adb_path(), ["devices", "-l"])
        worker.result.connect(self._on_devices_result)
        worker.finished.connect(worker.deleteLater)
        self._adb_worker = worker
        worker.start()

    def _on_devices_result(self, output: str, _ok: bool):
        blocker = QSignalBlocker(self._dev_combo)  # noqa: F841
        self._dev_combo.clear()
        self.device_list = []

        devices = []
        for line in output.splitlines()[1:]:
            line = line.strip()
            if not line: continue
            parts = line.split()
            if len(parts) < 2: continue
            serial, state = parts[0], parts[1]
            model = next((p.split(":")[1] for p in parts[2:] if p.startswith("model:")), "")
            devices.append((serial, state, model))

        if not devices:
            self._dev_status.setText(
                "⚠️ デバイスが見つかりません。\nUSBを接続してUSBデバッグを許可してください。")
            self._dev_status.setStyleSheet("color:#ff9800;font-size:11px;")
        else:
            for serial, state, model in devices:
                icon = "✅" if state == "device" else ("⚠️" if state == "offline" else "🔒")
                label = f"{icon} {model or serial}  ({serial})  [{state}]"
                self._dev_combo.addItem(label, serial)
                self.device_list.append((serial, state))
                if state == "offline":
                    QTimer.singleShot(50, self._show_offline_help)

            if len(devices) == 1:
                self._dev_combo.setCurrentIndex(0)
                self.settings["selected_device"] = devices[0][0]
            elif self.settings.get("selected_device"):
                for i in range(self._dev_combo.count()):
                    if self._dev_combo.itemData(i) == self.settings["selected_device"]:
                        self._dev_combo.setCurrentIndex(i); break

            self._dev_status.setText(f"✅ {len(devices)} 台検出")
            self._dev_status.setStyleSheet("color:#4CAF50;font-size:11px;")

        del blocker
        self._log_sig.emit(f"デバイス検索完了 ({len(devices)} 台)", "INFO")
        self._update_run_button()
        self._update_command_preview()

    def _show_offline_help(self):
        QMessageBox.information(self, "デバイスがオフライン状態",
            "デバイスが offline 状態です。\n\n"
            "【対処方法】\n"
            "1. USBケーブルを抜き差ししてください\n"
            "2. デバイスに「USBデバッグを許可しますか？」が表示されたら OK を押してください\n"
            "3. 設定 → 開発者オプション → USBデバッグ を OFF → ON にしてください\n"
            "4. adb を再起動: adb kill-server / adb start-server")

    # ── Wi-Fi 接続 ─────────────────────────────────────────
    def _wifi_connect(self):
        ip = self._wifi_ip.text().strip(); port = self._wifi_port.text().strip()
        if not ip:
            QMessageBox.warning(self, "入力エラー", "IP アドレスを入力してください"); return
        self._log_sig.emit(f"Wi-Fi 接続中: {ip}:{port}", "INFO")
        w = AdbWorker(self._adb_path(), ["connect", f"{ip}:{port}"])
        w.result.connect(lambda out, ok: (
            self._log_sig.emit(out, "INFO" if ok else "ERROR"),
            QTimer.singleShot(500, self._refresh_devices)))
        w.finished.connect(w.deleteLater); w.start()

    def _wifi_pair(self):
        ip = self._pair_ip.text().strip(); port = self._pair_port.text().strip()
        code = self._pair_code.text().strip()
        if not ip or not code:
            QMessageBox.warning(self, "入力エラー", "ペアリング IP とコードを入力してください"); return
        self._log_sig.emit(f"ペアリング中: {ip}:{port}", "INFO")
        w = AdbWorker(self._adb_path(), ["pair", f"{ip}:{port}", code])
        w.result.connect(lambda out, ok: self._log_sig.emit(out, "INFO" if ok else "ERROR"))
        w.finished.connect(w.deleteLater); w.start()

    # ── ファイル操作 ────────────────────────────────────────
    def _browse_scrcpy(self):
        p, _ = QFileDialog.getOpenFileName(self, "scrcpy.exe を選択", str(SCRIPT_DIR), "実行ファイル (*.exe)")
        if p: self._path_edit.setText(p)

    def _browse_record(self):
        fmt = self._rec_fmt.currentText()
        dflt = str(SCRIPT_DIR / f"scrcpy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{fmt}")
        p, _ = QFileDialog.getSaveFileName(self, "録画ファイルの保存先", dflt, f"動画 (*.{fmt})")
        if p: self._rec_file.setText(p); self._changed()

    def _use_default_rec_name(self):
        fmt = self._rec_fmt.currentText()
        self._rec_file.setText(
            str(SCRIPT_DIR / f"scrcpy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{fmt}"))
        self._changed()

    def _pick_bg(self):
        cur = self.settings.get("background_color", "")
        init = QColor(f"#{cur}") if cur else QColor("#000000")
        c = QColorDialog.getColor(init, self, "背景色を選択")
        if c.isValid():
            self._refresh_bg_btn(c.name().lstrip("#"))
            self._changed()

    def _clear_bg(self):
        self._refresh_bg_btn("")
        self._changed()

    # ── クリップボード ─────────────────────────────────────
    def _copy_command(self):
        QApplication.clipboard().setText(self._cmd_preview.text())
        self._log_sig.emit("コマンドをクリップボードにコピーしました", "INFO")

    def _copy_log(self):
        QApplication.clipboard().setText(self._log.toPlainText())

    def _clear_log(self):
        self._log.clear()

    # ── ログ ────────────────────────────────────────────────
    @pyqtSlot(str, str)
    def _append_log(self, msg: str, level: str):
        ts = datetime.now().strftime("%H:%M:%S")
        esc = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        color = {"ERROR": "#ef5350", "WARN": "#ffb74d"}.get(level, "#a0ff80")
        self._log.insertHtml(
            f'<span style="color:{color};">[{ts}] {esc}</span><br>')
        self._log.verticalScrollBar().setValue(
            self._log.verticalScrollBar().maximum())

    # ── scrcpy 実行 ─────────────────────────────────────────
    def _validate_launch(self) -> str | None:
        """起動前チェック。問題があればメッセージを返す"""
        if not self._scrcpy_path_valid():
            return "scrcpy.exe のパスが無効です。「📁 scrcpy パス」を確認してください。"
        s = self.settings
        if s.get("record_enabled") and not s.get("record_file"):
            return "録画ファイルのパスが指定されていません。"
        return None

    def _run_scrcpy(self):
        self._collect()
        err = self._validate_launch()
        if err:
            QMessageBox.warning(self, "起動エラー", err); return

        device = self._current_device()
        args   = build_args(self.settings, device)
        exe    = self.settings["scrcpy_path"]
        cmd_str = build_command_preview(self.settings, device)

        self._log_sig.emit(f"実行: {cmd_str}", "INFO")

        self._scrcpy = QProcess(self)
        self._scrcpy.readyReadStandardOutput.connect(self._proc_stdout)
        self._scrcpy.readyReadStandardError.connect(self._proc_stderr)
        self._scrcpy.finished.connect(self._proc_finished)
        self._scrcpy.errorOccurred.connect(self._proc_error)

        self._scrcpy.setProgram(exe)
        self._scrcpy.setArguments(args)
        self._scrcpy.start()

        if not self._scrcpy.waitForStarted(3000):
            self._log_sig.emit("scrcpy の起動に失敗しました", "ERROR")
            self._scrcpy = None
        self._update_run_button()

    def _stop_scrcpy(self):
        if self._scrcpy:
            self._scrcpy.terminate()
            QTimer.singleShot(3000, self._force_kill)

    def _force_kill(self):
        if self._scrcpy and self._scrcpy.state() != QProcess.NotRunning:
            self._scrcpy.kill()

    def _proc_stdout(self):
        if self._scrcpy:
            data = bytes(self._scrcpy.readAllStandardOutput()).decode("utf-8", errors="replace")
            for line in data.splitlines():
                if line.strip(): self._log_sig.emit(line.strip(), "INFO")

    def _proc_stderr(self):
        if self._scrcpy:
            data = bytes(self._scrcpy.readAllStandardError()).decode("utf-8", errors="replace")
            for line in data.splitlines():
                if line.strip():
                    lvl = "ERROR" if any(k in line.lower() for k in ("error", "failed", "could not")) else "INFO"
                    self._log_sig.emit(line.strip(), lvl)

    def _proc_finished(self, code, _status):
        self._log_sig.emit(f"scrcpy が終了しました (終了コード: {code})", "INFO")
        self._scrcpy = None
        self._update_run_button()

    def _proc_error(self, err):
        self._log_sig.emit(f"プロセスエラー: {err}", "ERROR")
        self._scrcpy = None
        self._update_run_button()

    # ── テーマ ──────────────────────────────────────────────
    def _toggle_theme(self):
        dark = self._theme_btn.isChecked()
        self.settings["dark_mode"] = dark
        self._sync_theme_btn_text()
        self._apply_theme()

    def _sync_theme_btn_text(self):
        dark = self.settings.get("dark_mode", True)
        self._theme_btn.setText("🌙 ダーク" if dark else "☀ ライト")

    def _apply_theme(self):
        QApplication.instance().setStyleSheet(
            DARK_STYLE if self.settings.get("dark_mode", True) else LIGHT_STYLE)

    # ── プリセット ─────────────────────────────────────────
    def _open_presets(self):
        self._collect()
        dlg = PresetDialog(self, self.presets, self.settings)
        dlg.exec_()
        self.presets = dlg.presets
        if dlg.loaded:
            # merge loaded preset onto defaults, then apply
            merged = dict(DEFAULT_SETTINGS)
            merged.update(dlg.loaded)
            merged["scrcpy_path"]     = self.settings.get("scrcpy_path", "")
            merged["onboarding_done"] = self.settings.get("onboarding_done", True)
            self.settings = merged
            self._apply_to_ui()
            self._update_command_preview()
            self._log_sig.emit("プリセットを読み込みました", "INFO")
        self._save_presets()

    # ── オンボーディング ───────────────────────────────────
    def _show_onboarding(self):
        OnboardingDialog(self).exec_()
        self.settings["onboarding_done"] = True
        self._save_settings()

    # ── 永続化 ─────────────────────────────────────────────
    def _load_settings(self):
        try:
            if SETTINGS_FILE.exists():
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                # Migrate: merge onto defaults so new keys always exist
                self.settings.update(loaded)
        except Exception as e:
            print(f"設定読み込みエラー: {e}")

    def _save_settings(self):
        try:
            self._collect()
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"設定保存エラー: {e}")

    def _load_presets(self):
        try:
            if PRESETS_FILE.exists():
                with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                    self.presets = json.load(f)
        except Exception as e:
            print(f"プリセット読み込みエラー: {e}")

    def _save_presets(self):
        try:
            with open(PRESETS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.presets, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"プリセット保存エラー: {e}")

    def closeEvent(self, event):
        if self._scrcpy and self._scrcpy.state() != QProcess.NotRunning:
            if QMessageBox.question(self, "終了確認",
                    "scrcpy が実行中です。終了しますか？",
                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                event.ignore(); return
            self._scrcpy.kill()
            self._scrcpy.waitForFinished(2000)
        self._save_settings()
        event.accept()


# ── エントリポイント ────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    font = QFont()
    for family in ("Yu Gothic UI", "Noto Sans JP", "Meiryo UI", "MS UI Gothic"):
        font.setFamily(family)
        if QFont(family).exactMatch():
            break
    font.setPointSize(9)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
