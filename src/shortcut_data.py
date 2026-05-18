# -*- coding: utf-8 -*-
"""scrcpy shortcut data based on the official GitHub docs."""

SHORTCUT_SOURCE_URL = "https://github.com/Genymobile/scrcpy/blob/master/doc/shortcuts.md"


def _t(ja: str, en: str) -> dict[str, str]:
    return {"ja": ja, "en": en}


SHORTCUT_SECTIONS = [
    {
        "title": _t("キーボードショートカット", "Keyboard shortcuts"),
        "items": [
            (_t("終了", "Quit"), "MOD + q"),
            (_t("全画面切り替え", "Switch fullscreen mode"), "MOD + f / F11"),
            (_t("表示を左に回転", "Rotate display left"), "MOD + ←"),
            (_t("表示を右に回転", "Rotate display right"), "MOD + →"),
            (_t("左右反転", "Flip display horizontally"), "MOD + Shift + ← / MOD + Shift + →"),
            (_t("上下反転", "Flip display vertically"), "MOD + Shift + ↑ / MOD + Shift + ↓"),
            (_t("表示を一時停止 / 再開", "Pause or re-pause display"), "MOD + z"),
            (_t("表示の一時停止を解除", "Unpause display"), "MOD + Shift + z"),
            (_t("映像キャプチャ / エンコードを再初期化", "Reset video capture/encoding"), "MOD + Shift + r"),
            (_t("ウィンドウを 1:1 にする", "Resize window to 1:1 (pixel-perfect)"), "MOD + g"),
            (_t("黒帯を削除する", "Resize window to remove black borders"), "MOD + w"),
            (_t("HOME を押す", "Click on HOME"), "MOD + h"),
            (_t("BACK を押す", "Click on BACK"), "MOD + b / MOD + Backspace"),
            (_t("APP_SWITCH を押す", "Click on APP_SWITCH"), "MOD + s"),
            (_t("MENU を押す（画面ロック解除）", "Click on MENU (unlock screen)"), "MOD + m"),
            (_t("音量を上げる", "Click on VOLUME_UP"), "MOD + ↑"),
            (_t("音量を下げる", "Click on VOLUME_DOWN"), "MOD + ↓"),
            (_t("POWER を押す", "Click on POWER"), "MOD + p"),
            (_t("端末画面をオンにする", "Turn device screen on"), "MOD + Shift + o"),
            (_t("端末画面をオフにする（ミラーリングは継続）", "Turn device screen off (keep mirroring)"), "MOD + o"),
            (_t("端末画面を回転", "Rotate device screen"), "MOD + r"),
            (_t("通知パネルを展開", "Expand notification panel"), "MOD + n"),
            (_t("設定パネルを展開", "Expand settings panel"), "MOD + n + n"),
            (_t("パネルを折りたたむ", "Collapse panels"), "MOD + Shift + n"),
            (_t("クリップボードへコピー", "Copy to clipboard"), "MOD + c"),
            (_t("クリップボードへ切り取り", "Cut to clipboard"), "MOD + x"),
            (_t("クリップボードを同期して貼り付け", "Synchronize clipboards and paste"), "MOD + v"),
            (_t("PC のクリップボード文字列を注入", "Inject computer clipboard text"), "MOD + Shift + v"),
            (_t("キーボード設定を開く（HID キーボードのみ）", "Open keyboard settings (HID keyboard only)"), "MOD + k"),
            (_t("FPS カウンターの表示切り替え", "Enable/disable FPS counter (on stdout)"), "MOD + i"),
            (_t("カメラのトーチをオン", "Turn on the camera torch (camera mode only)"), "MOD + t"),
            (_t("カメラのトーチをオフ", "Turn off the camera torch (camera mode only)"), "MOD + Shift + t"),
            (_t("カメラをズームイン", "Zoom camera in (camera mode only)"), "MOD + ↑"),
            (_t("カメラをズームアウト", "Zoom camera out (camera mode only)"), "MOD + ↓"),
        ],
    },
    {
        "title": _t("マウスショートカット", "Mouse shortcuts"),
        "items": [
            (_t("黒帯上をダブル左クリックで削除", "Double-left-click on black borders"), "Double-left-click"),
            (_t("中央クリックで HOME", "Middle-click"), "Middle-click"),
            (_t("右クリックで BACK（画面オフ時は電源オン）", "Right-click"), "Right-click"),
            (_t("4th ボタンで APP_SWITCH", "4th mouse button"), "4th-click"),
            (_t("5th ボタンで通知パネルを展開", "5th mouse button"), "5th-click"),
            (_t("Ctrl + ドラッグでピンチ操作 / 回転", "Ctrl + click-and-move"), "Ctrl + click-and-move"),
            (_t("Shift + ドラッグで縦方向の傾き", "Shift + click-and-move"), "Shift + click-and-move"),
            (_t("Ctrl + Shift + ドラッグで横方向の傾き", "Ctrl + Shift + click-and-move"), "Ctrl + Shift + click-and-move"),
            (_t("APK をドラッグ＆ドロップしてインストール", "Drag & drop APK file"), "Drop APK file"),
            (_t("APK 以外のファイルをドラッグ＆ドロップして push", "Drag & drop non-APK file"), "Drop non-APK file"),
        ],
    },
]


SHORTCUT_NOTES = [
    _t(
        "MOD は既定で左 Alt または左 Super です。`--shortcut-mod` で変更できます。",
        "MOD is left Alt or left Super by default. You can change it with `--shortcut-mod`.",
    ),
    _t(
        "同じキーを連続で使う操作は、いったん離してから再度押します。",
        "Repeated-key shortcuts are executed by releasing and pressing the key again.",
    ),
    _t(
        "Ctrl+キーのショートカットはデバイス側へ転送され、アプリ側で処理されます。",
        "All Ctrl+key shortcuts are forwarded to the device and handled by the active app.",
    ),
    _t(
        "右クリックは画面がオフなら電源オン、そうでなければ BACK を送ります。",
        "Right-click turns the screen on if it is off; otherwise it sends BACK.",
    ),
    _t(
        "4th / 5th ボタンは対応マウスでのみ利用できます。",
        "4th / 5th mouse buttons are only available on mice that have them.",
    ),
    _t(
        "コピー / 切り取り / 同期貼り付けは Android 7 以上で利用できます。",
        "Copy / cut / synchronized paste shortcuts require Android 7 or later.",
    ),
    _t(
        "MENU は React Native 開発時の開発メニューに使われることがあります。",
        "MENU may open the development menu in React Native apps.",
    ),
]
