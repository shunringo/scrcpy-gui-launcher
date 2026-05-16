# -*- coding: utf-8 -*-
"""scrcpy コマンド引数の生成"""

from pathlib import Path


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
    """UI表示用のコマンド文字列を返す"""
    exe   = Path(settings.get("scrcpy_path", "") or "scrcpy.exe").name
    args  = build_args(settings, device_serial)
    parts = [exe] + args
    return " ".join(f'"{p}"' if " " in p else p for p in parts)
