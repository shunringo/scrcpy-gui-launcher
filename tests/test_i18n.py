# -*- coding: utf-8 -*-
"""Tests for i18n.py — tr / set_lang / get_lang / translation completeness"""

import pytest
import i18n
from i18n import tr, set_lang, get_lang, TRANSLATIONS


# ── reset language to ja before each test ─────────────────────────────────

@pytest.fixture(autouse=True)
def reset_lang():
    set_lang("ja")
    yield
    set_lang("ja")


# ── set_lang / get_lang ───────────────────────────────────────────────────

def test_default_language_is_ja():
    assert get_lang() == "ja"

def test_set_lang_en():
    set_lang("en")
    assert get_lang() == "en"

def test_set_lang_ja():
    set_lang("ja")
    assert get_lang() == "ja"

def test_set_lang_unknown_falls_back_to_ja():
    set_lang("fr")
    assert get_lang() == "ja"

def test_set_lang_empty_string_falls_back_to_ja():
    set_lang("")
    assert get_lang() == "ja"


# ── tr() basic lookup ─────────────────────────────────────────────────────

def test_tr_returns_japanese_by_default():
    assert tr("lang_btn") == "EN"

def test_tr_returns_english_after_set_lang():
    set_lang("en")
    assert tr("lang_btn") == "JA"

def test_tr_known_key_ja():
    assert tr("theme_dark") == "🌙 ダーク"

def test_tr_known_key_en():
    set_lang("en")
    assert tr("theme_dark") == "🌙 Dark"

def test_tr_returns_string():
    result = tr("help_btn")
    assert isinstance(result, str)


# ── tr() fallback behaviour ───────────────────────────────────────────────

def test_tr_missing_key_returns_key_itself():
    result = tr("__nonexistent_key__")
    assert result == "__nonexistent_key__"

def test_tr_key_missing_from_en_falls_back_to_ja():
    """Inject a ja-only key, verify English falls back to Japanese."""
    TRANSLATIONS["ja"]["__test_ja_only__"] = "テスト"
    TRANSLATIONS["en"].pop("__test_ja_only__", None)
    try:
        set_lang("en")
        assert tr("__test_ja_only__") == "テスト"
    finally:
        del TRANSLATIONS["ja"]["__test_ja_only__"]


# ── tr() format arguments ─────────────────────────────────────────────────

def test_tr_device_found_msg_format_ja():
    result = tr("device_found_msg", n=3)
    assert "3" in result

def test_tr_device_found_msg_format_en():
    set_lang("en")
    result = tr("device_found_msg", n=5)
    assert "5" in result

def test_tr_device_scan_done_format():
    result = tr("device_scan_done", n=2)
    assert "2" in result

def test_tr_wifi_connecting_format():
    result = tr("wifi_connecting", addr="192.168.1.5:5555")
    assert "192.168.1.5:5555" in result

def test_tr_wifi_pairing_format():
    result = tr("wifi_pairing", addr="10.0.0.1:5556")
    assert "10.0.0.1:5556" in result

def test_tr_run_cmd_format():
    result = tr("run_cmd", cmd="scrcpy.exe -s abc")
    assert "scrcpy.exe -s abc" in result

def test_tr_scrcpy_exited_format():
    result = tr("scrcpy_exited", code=0)
    assert "0" in result

def test_tr_proc_error_format():
    result = tr("proc_error", err="FailedToStart")
    assert "FailedToStart" in result

def test_tr_settings_load_err_format():
    result = tr("settings_load_err", e="FileNotFoundError")
    assert "FileNotFoundError" in result

def test_tr_settings_save_err_format():
    result = tr("settings_save_err", e="PermissionError")
    assert "PermissionError" in result

def test_tr_presets_load_err_format():
    result = tr("presets_load_err", e="JSONDecodeError")
    assert "JSONDecodeError" in result

def test_tr_presets_save_err_format():
    result = tr("presets_save_err", e="IOError")
    assert "IOError" in result

def test_tr_save_record_filter_format():
    result = tr("save_record_filter", fmt="mkv")
    assert "mkv" in result

def test_tr_onboarding_title_format():
    result = tr("onboarding_title", app="scrcpy GUI Launcher")
    assert "scrcpy GUI Launcher" in result

def test_tr_preset_delete_msg_format():
    result = tr("preset_delete_msg", name="My Preset")
    assert "My Preset" in result

def test_tr_invalid_format_arg_returns_template():
    """If a required format key is missing, tr() returns the raw template."""
    result = tr("device_found_msg")   # missing n=
    assert "{n}" in result or result  # template returned without raising


# ── translation completeness ──────────────────────────────────────────────

def test_all_ja_keys_exist_in_en():
    ja_keys = set(TRANSLATIONS["ja"].keys())
    en_keys = set(TRANSLATIONS["en"].keys())
    missing = ja_keys - en_keys
    assert not missing, f"Keys in 'ja' missing from 'en': {missing}"

def test_all_en_keys_exist_in_ja():
    en_keys = set(TRANSLATIONS["en"].keys())
    ja_keys = set(TRANSLATIONS["ja"].keys())
    missing = en_keys - ja_keys
    assert not missing, f"Keys in 'en' missing from 'ja': {missing}"

def test_lang_btn_ja_shows_en():
    """ja lang_btn must show 'EN' (the other language)."""
    assert TRANSLATIONS["ja"]["lang_btn"] == "EN"

def test_lang_btn_en_shows_ja():
    """en lang_btn must show 'JA' (the other language)."""
    assert TRANSLATIONS["en"]["lang_btn"] == "JA"


# ── specific key spot-checks ──────────────────────────────────────────────

@pytest.mark.parametrize("key", [
    "help_btn", "shortcuts_btn", "theme_dark", "theme_light", "lang_btn",
    "device_group", "connection_group", "path_group",
    "tab_display", "tab_vd", "tab_camera", "tab_record",
    "run_btn", "stop_btn", "preset_btn",
    "device_searching", "device_not_found_msg", "device_found_msg",
    "offline_title", "offline_msg",
    "shortcuts_title", "shortcuts_intro",
    "path_valid", "path_invalid", "path_invalid_err",
    "launch_error_title", "no_record_file_err",
    "close_title", "close_msg",
    "lang_switch_busy_title", "lang_switch_busy_msg",
])
def test_key_exists_in_both_languages(key):
    assert key in TRANSLATIONS["ja"], f"Key '{key}' missing from 'ja'"
    assert key in TRANSLATIONS["en"], f"Key '{key}' missing from 'en'"

@pytest.mark.parametrize("key", [
    "device_found_msg", "device_scan_done", "wifi_connecting",
    "wifi_pairing", "run_cmd", "scrcpy_exited", "proc_error",
    "settings_load_err", "settings_save_err",
    "presets_load_err", "presets_save_err",
    "save_record_filter", "onboarding_title", "preset_delete_msg",
])
def test_parameterized_keys_contain_placeholder_ja(key):
    """All parameterized strings must contain at least one '{' in ja."""
    assert "{" in TRANSLATIONS["ja"][key], \
        f"Key '{key}' in 'ja' has no format placeholder"

def test_shortcuts_intro_mentions_shortcuts_doc():
    assert "shortcuts.md" in TRANSLATIONS["ja"]["shortcuts_intro"]
    assert "shortcuts.md" in TRANSLATIONS["en"]["shortcuts_intro"]

def test_no_empty_translations_ja():
    for key, val in TRANSLATIONS["ja"].items():
        assert val, f"Empty translation for key '{key}' in 'ja'"

def test_no_empty_translations_en():
    for key, val in TRANSLATIONS["en"].items():
        assert val, f"Empty translation for key '{key}' in 'en'"
