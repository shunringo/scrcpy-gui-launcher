# -*- coding: utf-8 -*-
"""Internationalization (i18n) — Japanese / English support.

Usage:
    from i18n import tr, set_lang

    tr("key")                   # simple lookup
    tr("device_found_msg", n=3) # with format args
"""

_lang: str = "ja"


def set_lang(lang: str) -> None:
    """Set active language. Falls back to 'ja' if unknown."""
    global _lang
    _lang = lang if lang in TRANSLATIONS else "ja"


def get_lang() -> str:
    return _lang


def tr(key: str, **kwargs) -> str:
    """Return translated string for *key* in the active language.

    Falls back to Japanese, then to the key itself if not found.
    Supports str.format() keyword arguments.
    """
    text = TRANSLATIONS.get(_lang, TRANSLATIONS["ja"]).get(key)
    if text is None:
        text = TRANSLATIONS["ja"].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text


TRANSLATIONS: dict[str, dict[str, str]] = {
    # ──────────────────────────────────────────────────────────────────────
    "ja": {
        # Header
        "help_btn":    "？ ヘルプ",
        "shortcuts_btn": "⌨ ショートカット",
        "theme_dark":  "🌙 ダーク",
        "theme_light": "☀ ライト",
        "lang_btn":    "EN",  # shows the OTHER language to switch to

        # Device group
        "device_group":               "📱 デバイス",
        "device_select_placeholder":  "デバイスを選択...",
        "device_not_found":           "デバイスが見つかりません",
        "refresh_devices_btn":        "🔄 デバイスを更新",

        # Connection group
        "connection_group": "🔌 新規デバイス接続",
        "usb_radio":        "USB 接続",
        "wifi_radio":       "Wi-Fi 接続",
        "ip_label":         "IP アドレス:",
        "port_label":       "ポート:",

        # Pairing group
        "pairing_group":        "ペアリング (Android 11+)",
        "pair_port_label":      "ペアリングポート:",
        "pair_code_label":      "ペアコード:",
        "pair_and_connect_btn": "🔑 ペアリングして接続",
        "pairing_help_btn":     "📖 Wi-Fi ペアリングの手順を確認",
        "pairing_help_title":   "Wi-Fi ペアリングの手順",
        "pairing_help_text": (
            "Android のワイヤレスデバッグでは\n"
            "「接続用ポート」と「ペアリング用ポート」の\n"
            "2つが使われます。\n\n"
            "① Android の設定 → 開発者向けオプション\n"
            "   →「ワイヤレスデバッグ」をオン\n\n"
            "② メイン画面に表示される\n"
            "   「IP アドレスとポート」を\n"
            "   上部の「IP アドレス」と「ポート」に入力\n\n"
            "③「デバイスのペア設定（コードを使用）」を\n"
            "   タップして表示される\n"
            "   「ポート」→「ペアリングポート」\n"
            "   「コード」→「ペアコード」に入力\n\n"
            "④「ペアリングして接続」を押す\n"
            "   → ペアリング後に自動で接続されます"
        ),

        # Path group
        "path_group":       "📁 scrcpy パス",
        "path_placeholder": "scrcpy.exe のパス",
        "browse_btn":       "📂 参照...",
        "path_valid":       "✅ scrcpy.exe を確認しました",
        "path_invalid":     "❌ scrcpy.exe が見つかりません",

        # Tabs
        "tab_display":  "🖥 表示",
        "tab_vd":       "📺 仮想画面",
        "tab_camera":   "📷 カメラ",
        "tab_record":   "⏺ 録画",

        # Command preview
        "cmd_preview_group": "💻 コマンドプレビュー",
        "copy_btn":          "📋 コピー",

        # Display tab – resolution group
        "res_group":      "解像度・フレームレート・ビットレート",
        "max_size_label": "最大解像度 (0=制限なし):",
        "no_limit":       "制限なし",
        "max_fps_label":  "最大 FPS:",
        "bitrate_label":  "ビットレート:",

        # Display tab – display options
        "display_opts_group": "表示オプション",
        "fullscreen_cb":  "フルスクリーン起動 (--fullscreen)",
        "always_top_cb":  "常に最前面 (--always-on-top)",
        "rotation_label": "画面回転:",
        "rotation_0":     "0° (変更なし)",
        "rotation_90":    "90°",
        "rotation_180":   "180°",
        "rotation_270":   "270°",
        "bg_color_label": "背景色 (--background-color):",
        "bg_clear_btn":   "クリア",
        "bg_select_btn":  "選択",

        # Display tab – behavior options
        "action_opts_group": "動作オプション",
        "no_audio_cb":   "音声なし (--no-audio)",
        "keep_alive_cb": "スリープ防止 (--keep-active)",
        "kill_adb_cb":   "終了時 ADB 停止 (--kill-adb-on-close)",

        # Virtual display tab
        "vd_camera_info":   "ℹ️  カメラモードが有効な場合、仮想ディスプレイは無効になります。",
        "new_display_cb":   "仮想ディスプレイを有効にする (--new-display)",
        "flex_display_cb":  "フレックスディスプレイ (--flex-display / -x)  ※ウィンドウサイズに追従",
        "vd_res_label":     "解像度 (W × H):",
        "dpi_label":        "DPI:",
        "start_app_label":  "起動アプリ (--start-app):",
        "start_app_placeholder": "例: com.android.settings",
        "no_vd_destroy_cb": "終了時コンテンツ保持 (--no-vd-destroy-content)",
        "no_vd_decor_cb":   "システムデコレーション非表示 (--no-vd-system-decorations)",

        # Camera tab
        "cam_info": (
            "ℹ️  カメラモード ON 時は通常のスクリーンミラーリングではなくカメラ映像を表示します。\n"
            "カメラモード ON 時、仮想ディスプレイ設定は無効になります。"
        ),
        "cam_mode_cb":     "カメラミラーリングを有効にする (--video-source=camera)",
        "cam_facing_label": "カメラ選択 (--camera-facing):",
        "cam_facing_rear":  "リア (back)",
        "cam_facing_front": "フロント (front)",
        "cam_zoom_label":   "ズーム (--camera-zoom):",
        "cam_torch_cb":     "トーチ（ライト）ON (--camera-torch)",

        # Record tab
        "record_cb":              "録画を有効にする (--record)",
        "record_file_label":      "出力ファイル:",
        "record_file_placeholder": "録画ファイルのパス",
        "record_default_name_btn": "📅 デフォルトファイル名を使用",
        "record_format_label":    "フォーマット:",
        "no_display_cb":          "録画中ミラーリング非表示 (--no-display)",

        # Footer
        "run_btn":    "▶  scrcpy を実行",
        "stop_btn":   "⏹  停止",
        "preset_btn": "⚙  プリセット",

        # Log area
        "log_header":   "📋 実行ログ",
        "log_clear_btn": "🗑 クリア",
        "log_copy_btn":  "📋 コピー",

        # Device status messages
        "device_searching":    "🔄 検索中...",
        "device_not_found_msg": (
            "⚠️ デバイスが見つかりません。\n"
            "USBを接続してUSBデバッグを許可してください。"
        ),
        "device_found_msg":  "✅ {n} 台検出",
        "device_scan_done":  "デバイス検索完了 ({n} 台)",

        # Dialogs
        "offline_title": "デバイスがオフライン状態",
        "offline_msg": (
            "デバイスが offline 状態です。\n\n"
            "【対処方法】\n"
            "1. USBケーブルを抜き差ししてください\n"
            "2. デバイスに「USBデバッグを許可しますか？」が表示されたら OK を押してください\n"
            "3. 設定 → 開発者オプション → USBデバッグ を OFF → ON にしてください\n"
            "4. adb を再起動: adb kill-server / adb start-server"
        ),
        "shortcuts_title": "scrcpy ショートカット一覧",
        "shortcuts_intro": (
            "scrcpy 公式の shortcuts.md を元にした、"
            "キーボードとマウス操作の一覧です。"
        ),
        "input_error":      "入力エラー",
        "no_ip_msg":        "IP アドレスを入力してください",
        "no_pair_info_msg":     "IP アドレス、ポート、ペアコードをすべて入力してください",
        "wifi_connecting":      "Wi-Fi 接続中: {addr}",
        "wifi_pairing":         "ペアリング中: {addr}",
        "wifi_pair_success":    "ペアリング成功。接続中: {addr}",

        # File dialogs
        "select_scrcpy_title":  "scrcpy.exe を選択",
        "select_scrcpy_filter": "実行ファイル (*.exe)",
        "save_record_title":    "録画ファイルの保存先",
        "save_record_filter":   "動画 (*.{fmt})",
        "select_bg_color_title": "背景色を選択",

        # Log messages
        "cmd_copied":         "コマンドをクリップボードにコピーしました",
        "run_cmd":            "実行: {cmd}",
        "scrcpy_start_failed": "scrcpy の起動に失敗しました",
        "scrcpy_exited":      "scrcpy が終了しました (終了コード: {code})",
        "proc_error":         "プロセスエラー: {err}",
        "preset_loaded":      "プリセットを読み込みました",

        # Launch errors
        "launch_error_title":  "起動エラー",
        "path_invalid_err":    "scrcpy.exe のパスが無効です。「📁 scrcpy パス」を確認してください。",
        "no_record_file_err":  "録画ファイルのパスが指定されていません。",

        # Close confirmation
        "close_title": "終了確認",
        "close_msg":   "scrcpy が実行中です。終了しますか？",

        # Settings / preset errors (printed to console only)
        "settings_load_err": "設定読み込みエラー: {e}",
        "settings_save_err": "設定保存エラー: {e}",
        "presets_load_err":  "プリセット読み込みエラー: {e}",
        "presets_save_err":  "プリセット保存エラー: {e}",

        # Language switch
        "lang_switch_busy_title": "切り替え不可",
        "lang_switch_busy_msg":   "scrcpy 実行中は言語を切り替えられません。",

        # Onboarding
        "onboarding_title": "ようこそ！ {app}",
        "onboarding_skip":  "スキップ",
        "onboarding_prev":  "◀ 前へ",
        "onboarding_next":  "次へ ▶",
        "onboarding_start": "✓ 始める",
        "onboarding_step1_icon":  "📱",
        "onboarding_step1_title": "Step 1: デバイスを接続する",
        "onboarding_step1_desc": (
            "AndroidデバイスをUSBケーブルでPCに接続してください。\n\n"
            "デバイス側で「USBデバッグ」を有効にする必要があります。\n"
            "設定 → 開発者オプション → USBデバッグ をONにしてください。\n\n"
            "※ 開発者オプションが表示されない場合は\n"
            "  設定 → 端末情報 → ビルド番号 を7回タップしてください。"
        ),
        "onboarding_step2_icon":  "⚙️",
        "onboarding_step2_title": "Step 2: scrcpy の設定をする",
        "onboarding_step2_desc": (
            "右側の設定タブから各種オプションを設定してください。\n\n"
            "• 表示タブ  ：解像度・FPS・ビットレートなどの表示設定\n"
            "• 仮想画面タブ：仮想ディスプレイの作成（v4.0新機能）\n"
            "• カメラタブ ：カメラ映像のミラーリング（v4.0新機能）\n"
            "• 録画タブ  ：画面録画の設定\n\n"
            "画面下部のコマンドプレビューで生成されるコマンドを確認できます。"
        ),
        "onboarding_step3_icon":  "▶️",
        "onboarding_step3_title": "Step 3: scrcpy を実行する",
        "onboarding_step3_desc": (
            "「🔄 デバイスを更新」ボタンでデバイスを検出し、\n"
            "「▶ scrcpy を実行」ボタンをクリックして起動してください。\n\n"
            "よく使う設定は「⚙ プリセット」から名前を付けて保存できます。\n\n"
            "実行ログエリアで scrcpy の出力をリアルタイムに確認できます。"
        ),

        # Preset dialog
        "preset_title":             "プリセット管理",
        "preset_saved_label":       "保存済みプリセット:",
        "preset_load_btn":          "📂 読み込み",
        "preset_save_btn":          "💾 現在の設定を保存",
        "preset_delete_btn":        "🗑 削除",
        "preset_add_defaults_label": "デフォルトプリセットを追加:",
        "preset_close_btn":         "閉じる",
        "preset_save_title":        "プリセット保存",
        "preset_save_name_label":   "プリセット名:",
        "preset_delete_title":      "削除確認",
        "preset_delete_msg":        '"{name}" を削除しますか？',
    },

    # ──────────────────────────────────────────────────────────────────────
    "en": {
        # Header
        "help_btn":    "? Help",
        "shortcuts_btn": "⌨ Shortcuts",
        "theme_dark":  "🌙 Dark",
        "theme_light": "☀ Light",
        "lang_btn":    "JA",

        # Device group
        "device_group":               "📱 Device",
        "device_select_placeholder":  "Select device...",
        "device_not_found":           "No device found",
        "refresh_devices_btn":        "🔄 Refresh devices",

        # Connection group
        "connection_group": "🔌 New device connection",
        "usb_radio":        "USB connection",
        "wifi_radio":       "Wi-Fi connection",
        "ip_label":         "IP address:",
        "port_label":       "Port:",

        # Pairing group
        "pairing_group":        "Pairing (Android 11+)",
        "pair_port_label":      "Pairing port:",
        "pair_code_label":      "Pair code:",
        "pair_and_connect_btn": "🔑 Pair & Connect",
        "pairing_help_btn":     "📖 Wi-Fi Pairing Guide",
        "pairing_help_title":   "Wi-Fi Pairing Guide",
        "pairing_help_text": (
            "Android wireless debugging uses two separate ports:\n"
            "one for pairing and one for connecting.\n\n"
            "① Go to Settings → Developer options\n"
            "   → Enable 'Wireless debugging'\n\n"
            "② On the main screen, note the\n"
            "   'IP address & Port' — enter them in\n"
            "   'IP address' and 'Port' above\n\n"
            "③ Tap 'Pair device with pairing code'\n"
            "   Enter the shown port → 'Pairing port'\n"
            "   Enter the shown code → 'Pair code'\n\n"
            "④ Press 'Pair & Connect'\n"
            "   → Automatically connects after pairing"
        ),

        # Path group
        "path_group":       "📁 scrcpy path",
        "path_placeholder": "Path to scrcpy.exe",
        "browse_btn":       "📂 Browse...",
        "path_valid":       "✅ scrcpy.exe found",
        "path_invalid":     "❌ scrcpy.exe not found",

        # Tabs
        "tab_display": "🖥 Display",
        "tab_vd":      "📺 Virtual display",
        "tab_camera":  "📷 Camera",
        "tab_record":  "⏺ Record",

        # Command preview
        "cmd_preview_group": "💻 Command preview",
        "copy_btn":          "📋 Copy",

        # Display tab – resolution group
        "res_group":      "Resolution / FPS / Bitrate",
        "max_size_label": "Max resolution (0=no limit):",
        "no_limit":       "No limit",
        "max_fps_label":  "Max FPS:",
        "bitrate_label":  "Bitrate:",

        # Display tab – display options
        "display_opts_group": "Display options",
        "fullscreen_cb":  "Fullscreen (--fullscreen)",
        "always_top_cb":  "Always on top (--always-on-top)",
        "rotation_label": "Rotation:",
        "rotation_0":     "0° (no change)",
        "rotation_90":    "90°",
        "rotation_180":   "180°",
        "rotation_270":   "270°",
        "bg_color_label": "Background color (--background-color):",
        "bg_clear_btn":   "Clear",
        "bg_select_btn":  "Select",

        # Display tab – behavior options
        "action_opts_group": "Behavior options",
        "no_audio_cb":   "No audio (--no-audio)",
        "keep_alive_cb": "Keep awake (--keep-active)",
        "kill_adb_cb":   "Kill ADB on close (--kill-adb-on-close)",

        # Virtual display tab
        "vd_camera_info":   "ℹ️  Virtual display is disabled when camera mode is active.",
        "new_display_cb":   "Enable virtual display (--new-display)",
        "flex_display_cb":  "Flex display (--flex-display / -x)  *follows window size",
        "vd_res_label":     "Resolution (W × H):",
        "dpi_label":        "DPI:",
        "start_app_label":  "Start app (--start-app):",
        "start_app_placeholder": "e.g. com.android.settings",
        "no_vd_destroy_cb": "Keep content on close (--no-vd-destroy-content)",
        "no_vd_decor_cb":   "No system decorations (--no-vd-system-decorations)",

        # Camera tab
        "cam_info": (
            "ℹ️  In camera mode, camera feed is shown instead of screen mirroring.\n"
            "Virtual display settings are disabled in camera mode."
        ),
        "cam_mode_cb":      "Enable camera mirroring (--video-source=camera)",
        "cam_facing_label": "Camera (--camera-facing):",
        "cam_facing_rear":  "Rear (back)",
        "cam_facing_front": "Front (front)",
        "cam_zoom_label":   "Zoom (--camera-zoom):",
        "cam_torch_cb":     "Torch ON (--camera-torch)",

        # Record tab
        "record_cb":               "Enable recording (--record)",
        "record_file_label":       "Output file:",
        "record_file_placeholder": "Path to recording file",
        "record_default_name_btn": "📅 Use default filename",
        "record_format_label":     "Format:",
        "no_display_cb":           "Hide display while recording (--no-display)",

        # Footer
        "run_btn":    "▶  Run scrcpy",
        "stop_btn":   "⏹  Stop",
        "preset_btn": "⚙  Presets",

        # Log area
        "log_header":    "📋 Log",
        "log_clear_btn": "🗑 Clear",
        "log_copy_btn":  "📋 Copy",

        # Device status messages
        "device_searching":    "🔄 Searching...",
        "device_not_found_msg": (
            "⚠️ No device found.\n"
            "Connect via USB and allow USB debugging."
        ),
        "device_found_msg": "✅ {n} device(s) found",
        "device_scan_done": "Device scan complete ({n} device(s))",

        # Dialogs
        "offline_title": "Device offline",
        "offline_msg": (
            "The device is in offline state.\n\n"
            "[Solutions]\n"
            "1. Unplug and replug the USB cable\n"
            "2. Tap OK on the device if 'Allow USB debugging?' appears\n"
            "3. Go to Settings → Developer options → Toggle USB debugging OFF then ON\n"
            "4. Restart adb: adb kill-server / adb start-server"
        ),
        "shortcuts_title": "scrcpy Shortcuts",
        "shortcuts_intro": (
            "This list is based on scrcpy's official shortcuts.md "
            "for keyboard and mouse control."
        ),
        "input_error":      "Input error",
        "no_ip_msg":        "Please enter an IP address",
        "no_pair_info_msg":     "Please enter IP address, ports, and pairing code",
        "wifi_connecting":      "Connecting Wi-Fi: {addr}",
        "wifi_pairing":         "Pairing: {addr}",
        "wifi_pair_success":    "Pairing successful. Connecting: {addr}",

        # File dialogs
        "select_scrcpy_title":  "Select scrcpy.exe",
        "select_scrcpy_filter": "Executable (*.exe)",
        "save_record_title":    "Save recording as",
        "save_record_filter":   "Video (*.{fmt})",
        "select_bg_color_title": "Select background color",

        # Log messages
        "cmd_copied":          "Command copied to clipboard",
        "run_cmd":             "Run: {cmd}",
        "scrcpy_start_failed": "Failed to launch scrcpy",
        "scrcpy_exited":       "scrcpy exited (code: {code})",
        "proc_error":          "Process error: {err}",
        "preset_loaded":       "Preset loaded",

        # Launch errors
        "launch_error_title":  "Launch error",
        "path_invalid_err":    "scrcpy.exe path is invalid. Check the '📁 scrcpy path' section.",
        "no_record_file_err":  "Recording file path is not set.",

        # Close confirmation
        "close_title": "Confirm exit",
        "close_msg":   "scrcpy is running. Exit?",

        # Settings / preset errors
        "settings_load_err": "Failed to load settings: {e}",
        "settings_save_err": "Failed to save settings: {e}",
        "presets_load_err":  "Failed to load presets: {e}",
        "presets_save_err":  "Failed to save presets: {e}",

        # Language switch
        "lang_switch_busy_title": "Cannot switch",
        "lang_switch_busy_msg":   "Cannot switch language while scrcpy is running.",

        # Onboarding
        "onboarding_title": "Welcome to {app}!",
        "onboarding_skip":  "Skip",
        "onboarding_prev":  "◀ Back",
        "onboarding_next":  "Next ▶",
        "onboarding_start": "✓ Get started",
        "onboarding_step1_icon":  "📱",
        "onboarding_step1_title": "Step 1: Connect a device",
        "onboarding_step1_desc": (
            "Connect your Android device to the PC via USB cable.\n\n"
            "You need to enable 'USB debugging' on the device.\n"
            "Go to Settings → Developer options → USB debugging and turn it ON.\n\n"
            "If Developer options is not visible:\n"
            "  Go to Settings → About phone → tap Build number 7 times."
        ),
        "onboarding_step2_icon":  "⚙️",
        "onboarding_step2_title": "Step 2: Configure scrcpy",
        "onboarding_step2_desc": (
            "Configure options in the tabs on the right.\n\n"
            "• Display tab    : Resolution, FPS, bitrate, etc.\n"
            "• Virtual display: Create a virtual display (v4.0 feature)\n"
            "• Camera tab     : Mirror camera feed (v4.0 feature)\n"
            "• Record tab     : Screen recording settings\n\n"
            "The command preview at the bottom shows the generated command."
        ),
        "onboarding_step3_icon":  "▶️",
        "onboarding_step3_title": "Step 3: Run scrcpy",
        "onboarding_step3_desc": (
            "Click '🔄 Refresh devices' to detect your device,\n"
            "then click '▶ Run scrcpy' to launch.\n\n"
            "Save frequently used settings as named presets via '⚙ Presets'.\n\n"
            "The log area shows scrcpy output in real time."
        ),

        # Preset dialog
        "preset_title":              "Preset manager",
        "preset_saved_label":        "Saved presets:",
        "preset_load_btn":           "📂 Load",
        "preset_save_btn":           "💾 Save current settings",
        "preset_delete_btn":         "🗑 Delete",
        "preset_add_defaults_label": "Add default presets:",
        "preset_close_btn":          "Close",
        "preset_save_title":         "Save preset",
        "preset_save_name_label":    "Preset name:",
        "preset_delete_title":       "Confirm deletion",
        "preset_delete_msg":         'Delete "{name}"?',
    },
}
