# -*- coding: utf-8 -*-
"""左パネル（デバイス・接続・パス設定）の UI 構築 Mixin"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QGroupBox, QRadioButton, QScrollArea,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config import APP_NAME, APP_VERSION
from i18n import tr


class LeftPanelMixin:
    """左パネルと共通ヘッダーの _mk_* メソッドを提供する Mixin。
    MainWindow に mix-in して使用する。
    """

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

        self._lang_btn = QPushButton(tr("lang_btn"))
        self._lang_btn.clicked.connect(self._switch_language)
        lay.addWidget(self._lang_btn)

        help_btn = QPushButton(tr("help_btn"))
        help_btn.clicked.connect(self._show_onboarding)
        lay.addWidget(help_btn)
        return w

    # ── 左パネル ───────────────────────────────────────────
    def _mk_left_panel(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(scroll.NoFrame)

        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(10, 10, 6, 10); lay.setSpacing(10)

        lay.addWidget(self._mk_device_group())
        lay.addWidget(self._mk_connection_group())
        lay.addWidget(self._mk_path_group())
        lay.addStretch()

        scroll.setWidget(inner)
        return scroll

    def _mk_device_group(self) -> QGroupBox:
        dg = QGroupBox(tr("device_group"))
        dl = QVBoxLayout(dg); dl.setSpacing(5)

        self._dev_combo = QComboBox()
        self._dev_combo.setPlaceholderText(tr("device_select_placeholder"))
        self._dev_combo.currentIndexChanged.connect(self._on_device_changed)
        dl.addWidget(self._dev_combo)

        self._dev_status = QLabel(tr("device_not_found"))
        self._dev_status.setWordWrap(True)
        self._dev_status.setStyleSheet("color:#ff9800;font-size:11px;")
        dl.addWidget(self._dev_status)

        ref_btn = QPushButton(tr("refresh_devices_btn"))
        ref_btn.clicked.connect(self._refresh_devices)
        dl.addWidget(ref_btn)
        return dg

    def _mk_connection_group(self) -> QGroupBox:
        cg = QGroupBox(tr("connection_group"))
        cl = QVBoxLayout(cg); cl.setSpacing(5)

        self._usb_rb  = QRadioButton(tr("usb_radio"))
        self._wifi_rb = QRadioButton(tr("wifi_radio"))
        is_wifi = self.settings.get("connection_type") == "wifi"
        self._usb_rb.setChecked(not is_wifi); self._wifi_rb.setChecked(is_wifi)
        self._usb_rb.toggled.connect(self._on_conn_type_changed)
        cl.addWidget(self._usb_rb); cl.addWidget(self._wifi_rb)

        self._wifi_box = QWidget()
        wl = QVBoxLayout(self._wifi_box)
        wl.setContentsMargins(0, 4, 0, 0); wl.setSpacing(4)
        wl.addWidget(QLabel(tr("ip_label")))
        self._wifi_ip = QLineEdit(self.settings.get("wifi_ip", "192.168.1."))
        self._wifi_ip.setPlaceholderText("192.168.1.xxx")
        wl.addWidget(self._wifi_ip)
        wl.addWidget(QLabel(tr("port_label")))
        self._wifi_port = QLineEdit(self.settings.get("wifi_port", "5555"))
        wl.addWidget(self._wifi_port)
        conn_btn = QPushButton(tr("connect_btn"))
        conn_btn.clicked.connect(self._wifi_connect)
        wl.addWidget(conn_btn)
        wl.addWidget(self._mk_pairing_group())

        cl.addWidget(self._wifi_box)
        self._wifi_box.setVisible(is_wifi)
        return cg

    def _mk_pairing_group(self) -> QGroupBox:
        pair_g = QGroupBox(tr("pairing_group"))
        pl = QVBoxLayout(pair_g); pl.setSpacing(4)
        pl.addWidget(QLabel(tr("pair_ip_label")))
        pr = QHBoxLayout()
        self._pair_ip   = QLineEdit(self.settings.get("pair_ip", ""))
        self._pair_ip.setPlaceholderText("192.168.1.x")
        self._pair_port = QLineEdit(self.settings.get("pair_port", "5556"))
        self._pair_port.setMaximumWidth(55)
        pr.addWidget(self._pair_ip); pr.addWidget(QLabel(":")); pr.addWidget(self._pair_port)
        pl.addLayout(pr)
        pl.addWidget(QLabel(tr("pair_code_label")))
        self._pair_code = QLineEdit(self.settings.get("pair_code", ""))
        self._pair_code.setPlaceholderText("123456")
        pl.addWidget(self._pair_code)
        pb = QPushButton(tr("pair_btn"))
        pb.clicked.connect(self._wifi_pair)
        pl.addWidget(pb)
        return pair_g

    def _mk_path_group(self) -> QGroupBox:
        pg = QGroupBox(tr("path_group"))
        pgl = QVBoxLayout(pg); pgl.setSpacing(4)
        self._path_edit = QLineEdit(self.settings.get("scrcpy_path", ""))
        self._path_edit.setPlaceholderText(tr("path_placeholder"))
        self._path_edit.textChanged.connect(self._on_path_changed)
        pgl.addWidget(self._path_edit)
        br = QPushButton(tr("browse_btn"))
        br.clicked.connect(self._browse_scrcpy)
        pgl.addWidget(br)
        self._path_status = QLabel()
        self._path_status.setWordWrap(True)
        self._path_status.setStyleSheet("font-size:11px;")
        pgl.addWidget(self._path_status)
        return pg
