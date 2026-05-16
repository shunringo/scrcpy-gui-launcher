# -*- coding: utf-8 -*-
"""ADB コマンドを別スレッドで実行するワーカー"""

import subprocess
import sys

from PyQt5.QtCore import QThread, pyqtSignal


class AdbWorker(QThread):
    result = pyqtSignal(str, bool)   # (output, success)

    def __init__(self, adb_path: str, args: list):
        super().__init__()
        self.adb_path = adb_path
        self.args     = args

    def run(self):
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        try:
            r = subprocess.run(
                [self.adb_path] + self.args,
                capture_output=True, text=True, timeout=15,
                creationflags=flags,
            )
            self.result.emit((r.stdout + r.stderr).strip(), r.returncode == 0)
        except Exception as e:
            self.result.emit(str(e), False)
