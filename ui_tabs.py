# -*- coding: utf-8 -*-
"""右パネル（設定タブ群・フッター・ログエリア）の UI 構築 Mixin"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QLineEdit, QSpinBox, QCheckBox,
    QTabWidget, QTextEdit, QGroupBox, QScrollArea, QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class TabsMixin:
    """右パネルと各設定タブの _mk_* メソッドを提供する Mixin。
    MainWindow に mix-in して使用する。
    """

    # ── 右パネル ───────────────────────────────────────────
    def _mk_right_panel(self) -> QWidget:
        panel = QWidget()
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(6, 10, 10, 6); lay.setSpacing(8)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._mk_display_tab(),  "🖥 表示")
        self._tabs.addTab(self._mk_vd_tab(),        "📺 仮想画面")
        self._tabs.addTab(self._mk_camera_tab(),    "📷 カメラ")
        self._tabs.addTab(self._mk_record_tab(),    "⏺ 録画")
        lay.addWidget(self._tabs, 1)

        cmd_g = QGroupBox("💻 コマンドプレビュー")
        cmd_l = QHBoxLayout(cmd_g)
        self._cmd_preview = QLineEdit()
        self._cmd_preview.setReadOnly(True)
        self._cmd_preview.setFont(QFont("Consolas", 10))
        copy_btn = QPushButton("📋 コピー")
        copy_btn.setMaximumWidth(78)
        copy_btn.clicked.connect(self._copy_command)
        cmd_l.addWidget(self._cmd_preview); cmd_l.addWidget(copy_btn)
        lay.addWidget(cmd_g)
        return panel

    # ── 表示タブ ───────────────────────────────────────────
    def _mk_display_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        w = QWidget()
        lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(8, 8, 8, 8)

        rg = QGroupBox("解像度・フレームレート・ビットレート")
        gl = self._mk_display_res_group(rg)  # noqa: F841
        lay.addWidget(rg)

        lay.addWidget(self._mk_display_options_group())
        lay.addWidget(self._mk_action_options_group())
        lay.addStretch()
        scroll.setWidget(w)
        return scroll

    def _mk_display_res_group(self, rg: QGroupBox):
        from PyQt5.QtWidgets import QGridLayout
        gl = QGridLayout(rg); gl.setColumnStretch(1, 1)

        gl.addWidget(QLabel("最大解像度 (0=制限なし):"), 0, 0)
        self._max_size = QSpinBox()
        self._max_size.setRange(0, 7680); self._max_size.setSingleStep(120)
        self._max_size.setValue(self.settings.get("max_size", 0))
        self._max_size.setSuffix(" px"); self._max_size.setSpecialValueText("制限なし")
        self._max_size.valueChanged.connect(self._changed)
        gl.addWidget(self._max_size, 0, 1)

        gl.addWidget(QLabel("最大 FPS:"), 1, 0)
        fps_row = QWidget(); frl = QHBoxLayout(fps_row); frl.setContentsMargins(0, 0, 0, 0)
        self._fps_sl = QSlider(Qt.Horizontal); self._fps_sl.setRange(1, 120)
        self._fps_sl.setValue(self.settings.get("max_fps", 60))
        self._fps_lbl = QLabel(f"{self.settings.get('max_fps', 60)} fps")
        self._fps_lbl.setMinimumWidth(48)
        self._fps_sl.valueChanged.connect(lambda v: (
            self._fps_lbl.setText(f"{v} fps"), self._changed()))
        frl.addWidget(self._fps_sl); frl.addWidget(self._fps_lbl)
        gl.addWidget(fps_row, 1, 1)

        gl.addWidget(QLabel("ビットレート:"), 2, 0)
        self._bitrate = QComboBox()
        self._bitrate.addItems(["1M", "2M", "4M", "8M", "16M", "20M", "32M"])
        idx = self._bitrate.findText(self.settings.get("video_bit_rate", "8M"))
        if idx >= 0: self._bitrate.setCurrentIndex(idx)
        self._bitrate.currentTextChanged.connect(self._changed)
        gl.addWidget(self._bitrate, 2, 1)
        return gl

    def _mk_display_options_group(self) -> QGroupBox:
        from PyQt5.QtWidgets import QGridLayout
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
        bg_row = QWidget(); brl = QHBoxLayout(bg_row); brl.setContentsMargins(0, 0, 0, 0)
        self._bg_btn = QPushButton(); self._bg_btn.setFixedWidth(56)
        self._bg_btn.clicked.connect(self._pick_bg)
        clr_btn = QPushButton("クリア"); clr_btn.setMaximumWidth(56)
        clr_btn.clicked.connect(self._clear_bg)
        brl.addWidget(self._bg_btn); brl.addWidget(clr_btn); brl.addStretch()
        dgl.addWidget(bg_row, 2, 1)
        self._refresh_bg_btn(self.settings.get("background_color", ""))
        return dg

    def _mk_action_options_group(self) -> QGroupBox:
        from PyQt5.QtWidgets import QGridLayout
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
        return og

    # ── 仮想画面タブ ───────────────────────────────────────
    def _mk_vd_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        w = QWidget()
        lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(8, 8, 8, 8)

        info = QLabel("ℹ️  カメラモードが有効な場合、仮想ディスプレイは無効になります。")
        info.setObjectName("infoLabel"); info.setWordWrap(True)
        lay.addWidget(info)

        self._new_disp = QCheckBox("仮想ディスプレイを有効にする (--new-display)")
        self._new_disp.setChecked(self.settings.get("new_display", False))
        self._new_disp.stateChanged.connect(self._on_new_disp_changed)
        lay.addWidget(self._new_disp)

        self._vd_box = QWidget()
        vbl = QVBoxLayout(self._vd_box)
        vbl.setContentsMargins(16, 0, 0, 0); vbl.setSpacing(8)

        self._flex_disp = QCheckBox("フレックスディスプレイ (--flex-display / -x)  ※ウィンドウサイズに追従")
        self._flex_disp.setChecked(self.settings.get("flex_display", False))
        self._flex_disp.stateChanged.connect(self._on_flex_changed)
        vbl.addWidget(self._flex_disp)

        self._vd_res_row = QWidget()
        rrl = QHBoxLayout(self._vd_res_row); rrl.setContentsMargins(0, 0, 0, 0)
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

        self._no_vd_dest  = QCheckBox("終了時コンテンツ保持 (--no-vd-destroy-content)")
        self._no_vd_decor = QCheckBox("システムデコレーション非表示 (--no-vd-system-decorations)")
        self._no_vd_dest.setChecked(self.settings.get("no_vd_destroy_content", False))
        self._no_vd_decor.setChecked(self.settings.get("no_vd_system_decorations", False))
        self._no_vd_dest.stateChanged.connect(self._changed)
        self._no_vd_decor.stateChanged.connect(self._changed)
        vbl.addWidget(self._no_vd_dest); vbl.addWidget(self._no_vd_decor)

        lay.addWidget(self._vd_box)
        self._vd_box.setEnabled(self.settings.get("new_display", False))
        self._vd_res_row.setVisible(not self.settings.get("flex_display", False))

        lay.addStretch()
        scroll.setWidget(w)
        return scroll

    # ── カメラタブ ─────────────────────────────────────────
    def _mk_camera_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        w = QWidget()
        lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(8, 8, 8, 8)

        info = QLabel("ℹ️  カメラモード ON 時は通常のスクリーンミラーリングではなくカメラ映像を表示します。\n"
                       "カメラモード ON 時、仮想ディスプレイ設定は無効になります。")
        info.setObjectName("infoLabel"); info.setWordWrap(True)
        lay.addWidget(info)

        self._cam_mode = QCheckBox("カメラミラーリングを有効にする (--video-source=camera)")
        self._cam_mode.setChecked(self.settings.get("camera_mode", False))
        self._cam_mode.stateChanged.connect(self._on_camera_mode_changed)
        lay.addWidget(self._cam_mode)

        self._cam_box = QWidget()
        cbl = QVBoxLayout(self._cam_box)
        cbl.setContentsMargins(16, 0, 0, 0); cbl.setSpacing(8)

        f_row = QHBoxLayout()
        f_row.addWidget(QLabel("カメラ選択 (--camera-facing):"))
        self._cam_facing = QComboBox()
        self._cam_facing.addItems(["リア (back)", "フロント (front)"])
        self._cam_facing.setCurrentIndex(0 if self.settings.get("camera_facing", "back") == "back" else 1)
        self._cam_facing.currentIndexChanged.connect(self._changed)
        f_row.addWidget(self._cam_facing); f_row.addStretch()
        cbl.addLayout(f_row)

        z_row = QHBoxLayout()
        z_row.addWidget(QLabel("ズーム (--camera-zoom):"))
        self._cam_zoom = QSlider(Qt.Horizontal); self._cam_zoom.setRange(0, 100)
        self._cam_zoom.setValue(self.settings.get("camera_zoom", 0))
        self._cam_zlbl = QLabel(f"{self.settings.get('camera_zoom', 0)}%")
        self._cam_zlbl.setMinimumWidth(36)
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
        lay.addStretch()
        scroll.setWidget(w)
        return scroll

    # ── 録画タブ ───────────────────────────────────────────
    def _mk_record_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        w = QWidget()
        lay = QVBoxLayout(w); lay.setSpacing(10); lay.setContentsMargins(8, 8, 8, 8)

        self._rec_cb = QCheckBox("録画を有効にする (--record)")
        self._rec_cb.setChecked(self.settings.get("record_enabled", False))
        self._rec_cb.stateChanged.connect(self._on_record_changed)
        lay.addWidget(self._rec_cb)

        self._rec_box = QWidget()
        rbl = QVBoxLayout(self._rec_box)
        rbl.setContentsMargins(16, 0, 0, 0); rbl.setSpacing(8)

        fp_row = QHBoxLayout()
        fp_row.addWidget(QLabel("出力ファイル:"))
        self._rec_file = QLineEdit(self.settings.get("record_file", ""))
        self._rec_file.setPlaceholderText("録画ファイルのパス")
        self._rec_file.textChanged.connect(self._changed)
        br = QPushButton("📂"); br.setMaximumWidth(34); br.clicked.connect(self._browse_record)
        fp_row.addWidget(self._rec_file); fp_row.addWidget(br)
        rbl.addLayout(fp_row)

        df_btn = QPushButton("📅 デフォルトファイル名を使用")
        df_btn.clicked.connect(self._use_default_rec_name)
        rbl.addWidget(df_btn)

        fmt_row = QHBoxLayout()
        fmt_row.addWidget(QLabel("フォーマット:"))
        self._rec_fmt = QComboBox()
        self._rec_fmt.addItems(["mp4", "mkv", "h264", "opus"])
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
        lay.addStretch()
        scroll.setWidget(w)
        return scroll

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

        preset_btn = QPushButton("⚙  プリセット")
        preset_btn.setMinimumHeight(42)
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
