#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scrcpy GUI Launcher v1.0
scrcpy v4.0 対応 GUI ランチャー — エントリポイント
"""

import sys

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QFont
except ImportError:
    print("PyQt5 が見つかりません。")
    print("pip install PyQt5  を実行してからもう一度起動してください。")
    input("Enterキーで終了...")
    sys.exit(1)

from config import APP_NAME, APP_VERSION
from main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    font = QFont()
    for family in ("Yu Gothic UI", "Noto Sans JP", "Meiryo UI", "MS UI Gothic"):
        font.setFamily(family)
        if QFont(family).exactMatch():
            break
    font.setPointSize(9)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
