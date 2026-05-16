# -*- coding: utf-8 -*-
"""Tests for command.py — build_args / build_command_preview"""

import pytest
from command import build_args, build_command_preview


# ── helpers ────────────────────────────────────────────────────────────────

def default_settings(**overrides) -> dict:
    """Return a minimal settings dict, optionally overriding keys."""
    base = {
        "scrcpy_path": "scrcpy.exe",
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
        "new_display": False,
        "flex_display": False,
        "vd_width": 1280,
        "vd_height": 720,
        "vd_dpi": 160,
        "start_app": "",
        "no_vd_destroy_content": False,
        "no_vd_system_decorations": False,
        "camera_mode": False,
        "camera_facing": "back",
        "camera_zoom": 0,
        "camera_torch": False,
        "record_enabled": False,
        "record_file": "",
        "record_format": "mp4",
        "no_display": False,
    }
    base.update(overrides)
    return base


# ── build_args: device serial ──────────────────────────────────────────────

def test_no_device_serial_omits_s_flag():
    args = build_args(default_settings(), "")
    assert "-s" not in args

def test_device_serial_adds_s_flag():
    args = build_args(default_settings(), "abc123")
    assert args[:2] == ["-s", "abc123"]

def test_wifi_device_serial_accepted():
    args = build_args(default_settings(), "192.168.1.5:5555")
    assert args[:2] == ["-s", "192.168.1.5:5555"]


# ── build_args: display settings ──────────────────────────────────────────

def test_max_size_zero_omitted():
    args = build_args(default_settings(max_size=0), "")
    assert "--max-size" not in args

def test_max_size_nonzero_included():
    args = build_args(default_settings(max_size=720), "")
    assert "--max-size" in args
    assert args[args.index("--max-size") + 1] == "720"

def test_max_fps_default_omitted():
    args = build_args(default_settings(max_fps=60), "")
    assert "--max-fps" not in args

def test_max_fps_nondefault_included():
    args = build_args(default_settings(max_fps=30), "")
    assert "--max-fps" in args
    assert args[args.index("--max-fps") + 1] == "30"

def test_bitrate_default_omitted():
    args = build_args(default_settings(video_bit_rate="8M"), "")
    assert "--video-bit-rate" not in args

def test_bitrate_nondefault_included():
    args = build_args(default_settings(video_bit_rate="4M"), "")
    assert "--video-bit-rate" in args
    assert args[args.index("--video-bit-rate") + 1] == "4M"

def test_fullscreen_flag():
    args = build_args(default_settings(fullscreen=True), "")
    assert "--fullscreen" in args

def test_fullscreen_disabled():
    args = build_args(default_settings(fullscreen=False), "")
    assert "--fullscreen" not in args

def test_always_on_top_flag():
    args = build_args(default_settings(always_on_top=True), "")
    assert "--always-on-top" in args

def test_rotation_zero_omitted():
    args = build_args(default_settings(rotation=0), "")
    assert "--rotation" not in args

@pytest.mark.parametrize("rot", [1, 2, 3])
def test_rotation_nonzero_included(rot):
    args = build_args(default_settings(rotation=rot), "")
    assert "--rotation" in args
    assert args[args.index("--rotation") + 1] == str(rot)

def test_no_audio_flag():
    args = build_args(default_settings(no_audio=True), "")
    assert "--no-audio" in args

def test_keep_active_flag():
    args = build_args(default_settings(keep_active=True), "")
    assert "--keep-active" in args

def test_kill_adb_on_close_flag():
    args = build_args(default_settings(kill_adb_on_close=True), "")
    assert "--kill-adb-on-close" in args

def test_background_color_included():
    args = build_args(default_settings(background_color="1a2b3c"), "")
    assert "--background-color" in args
    assert args[args.index("--background-color") + 1] == "#1a2b3c"

def test_background_color_empty_omitted():
    args = build_args(default_settings(background_color=""), "")
    assert "--background-color" not in args


# ── build_args: virtual display ───────────────────────────────────────────

def test_new_display_fixed_resolution():
    args = build_args(default_settings(
        new_display=True, flex_display=False,
        vd_width=1920, vd_height=1080, vd_dpi=240,
    ), "")
    assert "--new-display=1920x1080/240" in args
    assert "--flex-display" not in args

def test_new_display_flex():
    args = build_args(default_settings(
        new_display=True, flex_display=True, vd_dpi=200,
    ), "")
    assert "--new-display=/200" in args
    assert "--flex-display" in args

def test_new_display_default_dimensions():
    args = build_args(default_settings(new_display=True), "")
    assert "--new-display=1280x720/160" in args

def test_new_display_no_vd_destroy_content():
    args = build_args(default_settings(
        new_display=True, no_vd_destroy_content=True,
    ), "")
    assert "--no-vd-destroy-content" in args

def test_new_display_no_vd_system_decorations():
    args = build_args(default_settings(
        new_display=True, no_vd_system_decorations=True,
    ), "")
    assert "--no-vd-system-decorations" in args

def test_new_display_start_app():
    args = build_args(default_settings(
        new_display=True, start_app="com.example.app",
    ), "")
    assert "--start-app" in args
    assert args[args.index("--start-app") + 1] == "com.example.app"

def test_new_display_disabled():
    args = build_args(default_settings(new_display=False), "")
    assert not any("--new-display" in a for a in args)

def test_new_display_extras_omitted_when_disabled():
    """no_vd_destroy_content etc. are silently ignored when new_display=False."""
    args = build_args(default_settings(
        new_display=False, no_vd_destroy_content=True,
    ), "")
    assert "--no-vd-destroy-content" not in args

def test_new_display_suppressed_when_camera_mode():
    """camera_mode and new_display are mutually exclusive; camera wins."""
    args = build_args(default_settings(
        new_display=True, camera_mode=True,
    ), "")
    assert not any("--new-display" in a for a in args)


# ── build_args: camera ────────────────────────────────────────────────────

def test_camera_mode_back():
    args = build_args(default_settings(camera_mode=True, camera_facing="back"), "")
    assert "--video-source=camera" in args
    assert "--camera-facing=back" in args

def test_camera_mode_front():
    args = build_args(default_settings(camera_mode=True, camera_facing="front"), "")
    assert "--camera-facing=front" in args

def test_camera_mode_zoom_zero_omitted():
    args = build_args(default_settings(camera_mode=True, camera_zoom=0), "")
    assert not any("--camera-zoom" in a for a in args)

def test_camera_mode_zoom_nonzero():
    args = build_args(default_settings(camera_mode=True, camera_zoom=50), "")
    assert "--camera-zoom=50" in args

def test_camera_torch():
    args = build_args(default_settings(camera_mode=True, camera_torch=True), "")
    assert "--camera-torch" in args

def test_camera_mode_disabled():
    args = build_args(default_settings(camera_mode=False), "")
    assert "--video-source=camera" not in args


# ── build_args: recording ─────────────────────────────────────────────────

def test_record_mp4():
    args = build_args(default_settings(
        record_enabled=True, record_file="out.mp4", record_format="mp4",
    ), "")
    assert "--record" in args
    assert args[args.index("--record") + 1] == "out.mp4"
    assert "--record-format" not in args  # mp4 is default, omitted

def test_record_mkv_includes_format():
    args = build_args(default_settings(
        record_enabled=True, record_file="out.mkv", record_format="mkv",
    ), "")
    assert "--record-format" in args
    assert args[args.index("--record-format") + 1] == "mkv"

def test_record_no_display():
    args = build_args(default_settings(
        record_enabled=True, record_file="out.mp4", no_display=True,
    ), "")
    assert "--no-display" in args

def test_record_no_display_omitted_when_recording_disabled():
    """--no-display inside the record block only; ignored if record off."""
    args = build_args(default_settings(record_enabled=False, no_display=True), "")
    assert "--no-display" not in args

def test_record_disabled_no_record_args():
    args = build_args(default_settings(record_enabled=False), "")
    assert "--record" not in args

def test_record_enabled_but_no_file_skips_record():
    """record_file empty → record args omitted to prevent scrcpy errors."""
    args = build_args(default_settings(
        record_enabled=True, record_file="",
    ), "")
    assert "--record" not in args


# ── build_args: combined / ordering ──────────────────────────────────────

def test_all_simple_flags_together():
    args = build_args(default_settings(
        fullscreen=True, always_on_top=True, no_audio=True,
        keep_active=True, kill_adb_on_close=True,
    ), "")
    assert "--fullscreen" in args
    assert "--always-on-top" in args
    assert "--no-audio" in args
    assert "--keep-active" in args
    assert "--kill-adb-on-close" in args

def test_serial_is_first():
    args = build_args(default_settings(max_size=720, fullscreen=True), "myserial")
    assert args[0] == "-s"
    assert args[1] == "myserial"

def test_returns_list():
    result = build_args(default_settings(), "")
    assert isinstance(result, list)

def test_empty_settings_returns_empty_list():
    result = build_args({}, "")
    assert isinstance(result, list)


# ── build_command_preview ─────────────────────────────────────────────────

def test_preview_uses_exe_name_only():
    preview = build_command_preview(default_settings(scrcpy_path="C:/tools/scrcpy.exe"), "")
    assert preview.startswith("scrcpy.exe")

def test_preview_empty_path_fallback():
    preview = build_command_preview(default_settings(scrcpy_path=""), "")
    assert preview.startswith("scrcpy.exe")

def test_preview_quotes_args_with_spaces():
    preview = build_command_preview(default_settings(
        record_enabled=True, record_file="C:/my folder/out.mp4",
    ), "")
    assert '"C:/my folder/out.mp4"' in preview

def test_preview_no_quotes_for_simple_args():
    preview = build_command_preview(default_settings(max_size=720), "")
    assert '"720"' not in preview
    assert "720" in preview

def test_preview_includes_serial():
    preview = build_command_preview(default_settings(), "abc123")
    assert "-s" in preview
    assert "abc123" in preview

def test_preview_returns_string():
    result = build_command_preview(default_settings(), "")
    assert isinstance(result, str)
