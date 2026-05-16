# -*- coding: utf-8 -*-
"""Tests for config.py — constants, paths, DEFAULT_SETTINGS"""

import pytest
from pathlib import Path
import config
from config import (
    APP_NAME, APP_VERSION, SETTINGS_VERSION,
    APP_DIR, SETTINGS_FILE, PRESETS_FILE,
    SCRCPY_SEARCH_DIRS, DEFAULT_SETTINGS,
)


# ── constants ─────────────────────────────────────────────────────────────

def test_app_name_is_string():
    assert isinstance(APP_NAME, str) and APP_NAME

def test_app_version_is_string():
    assert isinstance(APP_VERSION, str) and APP_VERSION

def test_settings_version_is_int():
    assert isinstance(SETTINGS_VERSION, int) and SETTINGS_VERSION >= 1


# ── paths ─────────────────────────────────────────────────────────────────

def test_app_dir_is_path():
    assert isinstance(APP_DIR, Path)

def test_settings_file_under_app_dir():
    assert SETTINGS_FILE.parent == APP_DIR

def test_presets_file_under_app_dir():
    assert PRESETS_FILE.parent == APP_DIR

def test_settings_filename():
    assert SETTINGS_FILE.name == "scrcpy_launcher_settings.json"

def test_presets_filename():
    assert PRESETS_FILE.name == "scrcpy_launcher_presets.json"

def test_scrcpy_search_dirs_is_list():
    assert isinstance(SCRCPY_SEARCH_DIRS, list)
    assert len(SCRCPY_SEARCH_DIRS) > 0

def test_scrcpy_search_dirs_contains_app_dir():
    assert APP_DIR in SCRCPY_SEARCH_DIRS


# ── DEFAULT_SETTINGS structure ────────────────────────────────────────────

REQUIRED_KEYS = [
    "_version",
    "scrcpy_path",
    "connection_type",
    "wifi_ip", "wifi_port",
    "pair_port", "pair_code",
    "selected_device",
    "max_size", "max_fps", "video_bit_rate",
    "fullscreen", "always_on_top", "rotation",
    "no_audio", "keep_active", "kill_adb_on_close",
    "background_color",
    "new_display", "flex_display",
    "vd_width", "vd_height", "vd_dpi",
    "start_app", "no_vd_destroy_content", "no_vd_system_decorations",
    "camera_mode", "camera_facing", "camera_zoom", "camera_torch",
    "record_enabled", "record_file", "record_format", "no_display",
    "dark_mode", "onboarding_done", "language",
]

@pytest.mark.parametrize("key", REQUIRED_KEYS)
def test_default_settings_has_key(key):
    assert key in DEFAULT_SETTINGS, f"Missing key: {key}"

def test_default_settings_version_matches_constant():
    assert DEFAULT_SETTINGS["_version"] == SETTINGS_VERSION

def test_default_connection_type_is_usb():
    assert DEFAULT_SETTINGS["connection_type"] == "usb"

def test_default_max_size_zero():
    assert DEFAULT_SETTINGS["max_size"] == 0

def test_default_max_fps_60():
    assert DEFAULT_SETTINGS["max_fps"] == 60

def test_default_bitrate_8m():
    assert DEFAULT_SETTINGS["video_bit_rate"] == "8M"

def test_default_booleans_are_false():
    bool_false_keys = [
        "fullscreen", "always_on_top", "no_audio", "keep_active",
        "kill_adb_on_close", "new_display", "flex_display",
        "no_vd_destroy_content", "no_vd_system_decorations",
        "camera_mode", "camera_torch",
        "record_enabled", "no_display", "onboarding_done",
    ]
    for key in bool_false_keys:
        assert DEFAULT_SETTINGS[key] is False, f"{key} should default to False"

def test_default_dark_mode_true():
    assert DEFAULT_SETTINGS["dark_mode"] is True

def test_default_rotation_zero():
    assert DEFAULT_SETTINGS["rotation"] == 0

def test_default_camera_facing_back():
    assert DEFAULT_SETTINGS["camera_facing"] == "back"

def test_default_camera_zoom_zero():
    assert DEFAULT_SETTINGS["camera_zoom"] == 0

def test_default_record_format_mp4():
    assert DEFAULT_SETTINGS["record_format"] == "mp4"

def test_default_language_ja():
    assert DEFAULT_SETTINGS["language"] == "ja"

def test_default_vd_dimensions():
    assert DEFAULT_SETTINGS["vd_width"] == 1280
    assert DEFAULT_SETTINGS["vd_height"] == 720
    assert DEFAULT_SETTINGS["vd_dpi"] == 160

def test_default_wifi_port():
    assert DEFAULT_SETTINGS["wifi_port"] == "5555"

def test_default_pair_port():
    assert DEFAULT_SETTINGS["pair_port"] == "5556"

def test_default_settings_is_dict():
    assert isinstance(DEFAULT_SETTINGS, dict)

def test_default_settings_no_extra_none_values():
    """No setting should be None by default."""
    for key, val in DEFAULT_SETTINGS.items():
        assert val is not None, f"DEFAULT_SETTINGS['{key}'] is None"
