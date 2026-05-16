# -*- coding: utf-8 -*-
"""MainWindow — アプリケーションロジック"""

import json
import re
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QMessageBox, QFileDialog, QColorDialog,
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer, QProcess, QSignalBlocker

import i18n
from i18n import tr
from config import (
    APP_NAME, APP_VERSION, APP_DIR, SCRCPY_SEARCH_DIRS,
    SETTINGS_FILE, PRESETS_FILE, DEFAULT_SETTINGS,
)
from command import build_args, build_command_preview
from adb import AdbWorker
from themes import DARK_STYLE, LIGHT_STYLE
from dialogs import OnboardingDialog, PresetDialog
from ui_panels import LeftPanelMixin
from ui_tabs import TabsMixin


def _is_wifi_serial(serial: str) -> bool:
    """ADB シリアルが Wi-Fi 接続かどうかを判定する。

    対応形式:
    - 従来の adb connect: 192.168.1.10:5555  （host:port）
    - Android 11+ ワイヤレスデバッグ: adb-XXXX._adb-tls-connect._tcp
    """
    if "._adb-tls-connect._tcp" in serial:
        return True
    if re.match(r'.+:\d+$', serial):
        return True
    return False


class MainWindow(LeftPanelMixin, TabsMixin, QMainWindow):
    _log_sig = pyqtSignal(str, str)   # (message, level)

    def __init__(self):
        super().__init__()
        self.settings: dict = dict(DEFAULT_SETTINGS)
        self.presets:  dict = {}
        self.device_list: list = []   # list of (serial, state, model)
        self._scrcpy: QProcess | None = None
        self._adb_worker: AdbWorker | None = None
        self._pair_worker: AdbWorker | None = None
        self._connect_worker: AdbWorker | None = None
        self._init_done = False

        self._load_settings()
        self._load_presets()
        self._find_scrcpy()

        # Apply saved language BEFORE building UI
        i18n.set_lang(self.settings.get("language", "ja"))

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

    # ── パス解決 ──────────────────────────────────────────
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
        left.setMinimumWidth(230); left.setMaximumWidth(270)
        hlay.addWidget(left)
        sep = QFrame(); sep.setFrameShape(QFrame.VLine); sep.setFrameShadow(QFrame.Sunken)
        hlay.addWidget(sep)
        hlay.addWidget(self._mk_right_panel(), 1)

        vlay.addWidget(body, 1)
        vlay.addWidget(self._mk_footer())
        vlay.addWidget(self._mk_log_area())

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
        s["no_vd_destroy_content"]    = self._no_vd_dest.isChecked()
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
            self._wifi_ip, self._wifi_port, self._pair_port, self._pair_code,
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
        self._vd_box.setEnabled(self._new_disp.isChecked())
        self._changed()

    def _on_flex_changed(self):
        self._vd_res_row.setVisible(not self._flex_disp.isChecked())
        self._changed()

    def _on_camera_mode_changed(self):
        self._cam_box.setEnabled(self._cam_mode.isChecked())
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
            self._path_status.setText(tr("path_valid"))
            self._path_status.setStyleSheet("color:#4CAF50;font-size:11px;")
        else:
            self._path_status.setText(tr("path_invalid"))
            self._path_status.setStyleSheet("color:#ef5350;font-size:11px;")
        self._update_run_button()

    def _refresh_bg_btn(self, color: str):
        self.settings["background_color"] = color
        if color:
            self._bg_btn.setStyleSheet(f"background-color:#{color};border:1px solid #888;")
            self._bg_btn.setText(f"#{color}")
        else:
            self._bg_btn.setStyleSheet("")
            self._bg_btn.setText(tr("bg_select_btn"))

    # ── デバイス管理 ────────────────────────────────────────
    def _refresh_devices(self):
        self._dev_status.setText(tr("device_searching"))
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
            self._dev_status.setText(tr("device_not_found_msg"))
            self._dev_status.setStyleSheet("color:#ff9800;font-size:11px;")
        else:
            for serial, state, model in devices:
                status_icon = "✅" if state == "device" else ("⚠️" if state == "offline" else "🔒")
                conn_tag = "[Wi-Fi]" if _is_wifi_serial(serial) else "[USB]"
                label = f"{status_icon} {conn_tag} {model or serial}  ({serial})  [{state}]"
                self._dev_combo.addItem(label, serial)
                self.device_list.append((serial, state, model))
                if state == "offline":
                    QTimer.singleShot(50, self._show_offline_help)

            if len(devices) == 1:
                self._dev_combo.setCurrentIndex(0)
                self.settings["selected_device"] = devices[0][0]
            elif self.settings.get("selected_device"):
                for i in range(self._dev_combo.count()):
                    if self._dev_combo.itemData(i) == self.settings["selected_device"]:
                        self._dev_combo.setCurrentIndex(i); break

            self._dev_status.setText(tr("device_found_msg", n=len(devices)))
            self._dev_status.setStyleSheet("color:#4CAF50;font-size:11px;")

        del blocker
        self._log_sig.emit(tr("device_scan_done", n=len(devices)), "INFO")
        self._adb_worker = None
        self._update_run_button()
        self._update_command_preview()

    def _show_offline_help(self):
        QMessageBox.information(self, tr("offline_title"), tr("offline_msg"))

    # ── Wi-Fi 接続 ─────────────────────────────────────────
    def _show_pairing_help(self):
        QMessageBox.information(self, tr("pairing_help_title"), tr("pairing_help_text"))

    def _wifi_pair(self):
        # 実行中の場合は多重起動を防ぐ
        if self._pair_worker is not None or self._connect_worker is not None:
            return
        ip = self._wifi_ip.text().strip()
        pair_port = self._pair_port.text().strip()
        conn_port = self._wifi_port.text().strip()
        code = self._pair_code.text().strip()
        if not ip or not pair_port or not conn_port or not code:
            QMessageBox.warning(self, tr("input_error"), tr("no_pair_info_msg")); return
        self._pair_btn.setEnabled(False)
        self._log_sig.emit(tr("wifi_pairing", addr=f"{ip}:{pair_port}"), "INFO")
        self._pair_worker = AdbWorker(self._adb_path(), ["pair", f"{ip}:{pair_port}", code])

        def _on_pair_done(out: str, ok: bool):
            self._log_sig.emit(out, "INFO" if ok else "ERROR")
            self._pair_worker = None
            if ok and "successfully" in out.lower():
                self._log_sig.emit(tr("wifi_pair_success", addr=f"{ip}:{conn_port}"), "INFO")
                self._connect_worker = AdbWorker(self._adb_path(), ["connect", f"{ip}:{conn_port}"])

                def _on_connect_done(o: str, ok2: bool):
                    self._log_sig.emit(o, "INFO" if ok2 else "ERROR")
                    self._connect_worker = None
                    self._pair_btn.setEnabled(True)
                    QTimer.singleShot(500, self._refresh_devices)

                self._connect_worker.result.connect(_on_connect_done)
                self._connect_worker.finished.connect(self._connect_worker.deleteLater)
                self._connect_worker.start()
            else:
                self._pair_btn.setEnabled(True)

        self._pair_worker.result.connect(_on_pair_done)
        self._pair_worker.finished.connect(self._pair_worker.deleteLater)
        self._pair_worker.start()

    # ── ファイル操作 ────────────────────────────────────────
    def _browse_scrcpy(self):
        p, _ = QFileDialog.getOpenFileName(
            self, tr("select_scrcpy_title"), str(APP_DIR), tr("select_scrcpy_filter"))
        if p: self._path_edit.setText(p)

    def _browse_record(self):
        fmt  = self._rec_fmt.currentText()
        dflt = str(APP_DIR / f"scrcpy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{fmt}")
        p, _ = QFileDialog.getSaveFileName(self, tr("save_record_title"), dflt, tr("save_record_filter", fmt=fmt))
        if p:
            self._rec_file.setText(p)
            self._changed()

    def _use_default_rec_name(self):
        fmt = self._rec_fmt.currentText()
        self._rec_file.setText(
            str(APP_DIR / f"scrcpy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{fmt}"))
        self._changed()

    def _pick_bg(self):
        from PyQt5.QtGui import QColor
        cur  = self.settings.get("background_color", "")
        init = QColor(f"#{cur}") if cur else QColor("#000000")
        c = QColorDialog.getColor(init, self, tr("select_bg_color_title"))
        if c.isValid():
            self._refresh_bg_btn(c.name().lstrip("#"))
            self._changed()

    def _clear_bg(self):
        self._refresh_bg_btn("")
        self._changed()

    # ── クリップボード ─────────────────────────────────────
    def _copy_command(self):
        QApplication.clipboard().setText(self._cmd_preview.text())
        self._log_sig.emit(tr("cmd_copied"), "INFO")

    def _copy_log(self):
        QApplication.clipboard().setText(self._log.toPlainText())

    def _clear_log(self):
        self._log.clear()

    # ── ログ ────────────────────────────────────────────────
    @pyqtSlot(str, str)
    def _append_log(self, msg: str, level: str):
        ts  = datetime.now().strftime("%H:%M:%S")
        esc = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        color = {"ERROR": "#ef5350", "WARN": "#ffb74d"}.get(level, "#a0ff80")
        self._log.insertHtml(
            f'<span style="color:{color};">[{ts}] {esc}</span><br>')
        self._log.verticalScrollBar().setValue(
            self._log.verticalScrollBar().maximum())

    # ── scrcpy 実行 ─────────────────────────────────────────
    def _validate_launch(self) -> str | None:
        if not self._scrcpy_path_valid():
            return tr("path_invalid_err")
        s = self.settings
        if s.get("record_enabled") and not s.get("record_file"):
            return tr("no_record_file_err")
        return None

    def _run_scrcpy(self):
        self._collect()
        err = self._validate_launch()
        if err:
            QMessageBox.warning(self, tr("launch_error_title"), err); return

        device  = self._current_device()
        args    = build_args(self.settings, device)
        exe     = self.settings["scrcpy_path"]
        cmd_str = build_command_preview(self.settings, device)

        self._log_sig.emit(tr("run_cmd", cmd=cmd_str), "INFO")

        self._scrcpy = QProcess(self)
        self._scrcpy.readyReadStandardOutput.connect(self._proc_stdout)
        self._scrcpy.readyReadStandardError.connect(self._proc_stderr)
        self._scrcpy.finished.connect(self._proc_finished)
        self._scrcpy.errorOccurred.connect(self._proc_error)
        self._scrcpy.setProgram(exe)
        self._scrcpy.setArguments(args)
        self._scrcpy.start()

        if not self._scrcpy.waitForStarted(3000):
            self._log_sig.emit(tr("scrcpy_start_failed"), "ERROR")
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
        self._log_sig.emit(tr("scrcpy_exited", code=code), "INFO")
        self._scrcpy = None
        self._update_run_button()

    def _proc_error(self, err):
        self._log_sig.emit(tr("proc_error", err=err), "ERROR")
        self._scrcpy = None
        self._update_run_button()

    # ── 言語切替 ────────────────────────────────────────────
    def _switch_language(self):
        if self._scrcpy and self._scrcpy.state() != QProcess.NotRunning:
            QMessageBox.information(self, tr("lang_switch_busy_title"), tr("lang_switch_busy_msg"))
            return
        self._collect()
        self.settings["language"] = "en" if self.settings.get("language", "ja") == "ja" else "ja"
        i18n.set_lang(self.settings["language"])
        self._save_settings()
        self._rebuild_ui()

    def _rebuild_ui(self):
        log_html = self._log.toHtml()
        tab_idx  = self._tabs.currentIndex()
        cached_devices = list(self.device_list)

        if self._adb_worker:
            try: self._adb_worker.result.disconnect()
            except (TypeError, RuntimeError): pass
            self._adb_worker = None

        self._init_done = False
        self._build_ui()
        self._apply_theme()
        self._init_done = True
        self._apply_to_ui()
        self._repopulate_devices(cached_devices)
        self._log.setHtml(log_html)
        self._tabs.setCurrentIndex(tab_idx)
        self._update_command_preview()
        self._validate_scrcpy_path()
        self._update_run_button()

    def _repopulate_devices(self, cached_devices: list):
        from PyQt5.QtCore import QSignalBlocker as SB
        blocker = SB(self._dev_combo)  # noqa: F841
        self._dev_combo.clear()
        self.device_list = []
        for serial, state, model in cached_devices:
            status_icon = "✅" if state == "device" else ("⚠️" if state == "offline" else "🔒")
            conn_tag = "[Wi-Fi]" if _is_wifi_serial(serial) else "[USB]"
            label = f"{status_icon} {conn_tag} {model or serial}  ({serial})  [{state}]"
            self._dev_combo.addItem(label, serial)
            self.device_list.append((serial, state, model))
        if self.device_list:
            self._dev_status.setText(tr("device_found_msg", n=len(self.device_list)))
            self._dev_status.setStyleSheet("color:#4CAF50;font-size:11px;")
            sel = self.settings.get("selected_device")
            if sel:
                for i in range(self._dev_combo.count()):
                    if self._dev_combo.itemData(i) == sel:
                        self._dev_combo.setCurrentIndex(i); break

    # ── テーマ ──────────────────────────────────────────────
    def _toggle_theme(self):
        dark = self._theme_btn.isChecked()
        self.settings["dark_mode"] = dark
        self._sync_theme_btn_text()
        self._apply_theme()

    def _sync_theme_btn_text(self):
        dark = self.settings.get("dark_mode", True)
        self._theme_btn.setText(tr("theme_dark") if dark else tr("theme_light"))

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
            merged = dict(DEFAULT_SETTINGS)
            merged.update(dlg.loaded)
            merged["scrcpy_path"]     = self.settings.get("scrcpy_path", "")
            merged["onboarding_done"] = self.settings.get("onboarding_done", True)
            self.settings = merged
            self._apply_to_ui()
            self._update_command_preview()
            self._log_sig.emit(tr("preset_loaded"), "INFO")
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
                self.settings.update(loaded)
                # 旧キーのマイグレーション: pair_ip は wifi_ip に統合済み
                self.settings.pop("pair_ip", None)
        except Exception as e:
            print(tr("settings_load_err", e=e))

    def _save_settings(self):
        try:
            self._collect()
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(tr("settings_save_err", e=e))

    def _load_presets(self):
        try:
            if PRESETS_FILE.exists():
                with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                    self.presets = json.load(f)
        except Exception as e:
            print(tr("presets_load_err", e=e))

    def _save_presets(self):
        try:
            with open(PRESETS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.presets, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(tr("presets_save_err", e=e))

    def closeEvent(self, event):
        if self._scrcpy and self._scrcpy.state() != QProcess.NotRunning:
            if QMessageBox.question(self, tr("close_title"), tr("close_msg"),
                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                event.ignore(); return
            self._scrcpy.kill()
            self._scrcpy.waitForFinished(2000)
        for worker in (self._pair_worker, self._connect_worker):
            if worker is not None:
                worker.quit()
                worker.wait(2000)
        self._save_settings()
        event.accept()
