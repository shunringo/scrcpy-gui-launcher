# -*- coding: utf-8 -*-
"""定数・パス解決・デフォルト設定"""

import sys
from pathlib import Path

# ── パス解決 ────────────────────────────────────────────
if getattr(sys, "frozen", False):
    SCRIPT_DIR = Path(sys.executable).parent.resolve()
else:
    SCRIPT_DIR = Path(__file__).parent.resolve()

# launcher/ サブフォルダ構成の場合、scrcpy 本体は親フォルダにある
SCRCPY_SEARCH_DIRS = [SCRIPT_DIR.parent, SCRIPT_DIR]

SETTINGS_FILE    = SCRIPT_DIR / "scrcpy_launcher_settings.json"
PRESETS_FILE     = SCRIPT_DIR / "scrcpy_launcher_presets.json"

APP_NAME         = "scrcpy GUI Launcher"
APP_VERSION      = "1.0"
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
