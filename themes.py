# -*- coding: utf-8 -*-
"""UI テーマ定義（ダーク / ライト）"""

DARK_STYLE = """
QWidget { background-color:#1a1a2e; color:#e0e0e0;
  font-family:"Yu Gothic UI","Noto Sans JP","Meiryo UI",sans-serif; }
QMainWindow, QDialog { background-color:#1a1a2e; }
QGroupBox { border:1px solid #3a3a5c; border-radius:6px; margin-top:8px;
  padding-top:8px; color:#a0a0c0; font-weight:bold; }
QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 4px; }
QPushButton { background-color:#16213e; color:#e0e0e0; border:1px solid #4a4a7a;
  border-radius:5px; padding:5px 12px; min-height:22px; }
QPushButton:hover { background-color:#0f3460; border-color:#4CAF50; }
QPushButton:pressed { background-color:#0a2840; }
QPushButton:disabled { background-color:#2a2a4a; color:#606080; border-color:#3a3a5a; }
QPushButton#runButton { background-color:#1b5e20; color:#fff; border:1px solid #4CAF50;
  font-weight:bold; font-size:13px; padding:8px 22px; }
QPushButton#runButton:hover { background-color:#2e7d32; }
QPushButton#runButton:disabled { background-color:#2a2a4a; border-color:#3a3a5a; }
QPushButton#stopButton { background-color:#7f0000; color:#fff; border:1px solid #ef5350;
  font-weight:bold; font-size:13px; padding:8px 22px; }
QPushButton#stopButton:hover { background-color:#b71c1c; }
QComboBox { background-color:#16213e; color:#e0e0e0; border:1px solid #4a4a7a;
  border-radius:4px; padding:4px 8px; min-height:22px; }
QComboBox::drop-down { border:none; width:18px; }
QComboBox QAbstractItemView { background-color:#16213e; color:#e0e0e0;
  selection-background-color:#0f3460; border:1px solid #4a4a7a; }
QLineEdit, QSpinBox { background-color:#16213e; color:#e0e0e0; border:1px solid #4a4a7a;
  border-radius:4px; padding:4px 8px; min-height:22px; }
QLineEdit:focus, QSpinBox:focus { border-color:#4CAF50; }
QLineEdit:read-only { background-color:#12121e; color:#80ff60; }
QTabWidget::pane { border:1px solid #3a3a5c; border-radius:4px; }
QTabBar::tab { background-color:#16213e; color:#a0a0c0; border:1px solid #3a3a5c;
  padding:6px 14px; border-radius:4px 4px 0 0; }
QTabBar::tab:selected { background-color:#0f3460; color:#4CAF50;
  border-bottom:2px solid #4CAF50; }
QTabBar::tab:hover:!selected { background-color:#1a3050; color:#e0e0e0; }
QSlider::groove:horizontal { height:6px; background:#3a3a5c; border-radius:3px; }
QSlider::handle:horizontal { background:#4CAF50; width:16px; height:16px;
  margin:-5px 0; border-radius:8px; }
QSlider::sub-page:horizontal { background:#4CAF50; border-radius:3px; }
QCheckBox { color:#e0e0e0; spacing:6px; }
QCheckBox::indicator { width:16px; height:16px; border:1px solid #4a4a7a;
  border-radius:3px; background-color:#16213e; }
QCheckBox::indicator:checked { background-color:#4CAF50; border-color:#4CAF50; }
QRadioButton { color:#e0e0e0; spacing:6px; }
QRadioButton::indicator { width:14px; height:14px; border:1px solid #4a4a7a;
  border-radius:7px; background-color:#16213e; }
QRadioButton::indicator:checked { background-color:#4CAF50; border-color:#4CAF50; }
QTextEdit { background-color:#0d0d1a; color:#a0ff80; border:1px solid #3a3a5c;
  border-radius:4px; font-family:"Consolas","Courier New",monospace; font-size:11px; }
QScrollBar:vertical { background:#1a1a2e; width:10px; border-radius:5px; }
QScrollBar::handle:vertical { background:#4a4a7a; border-radius:5px; min-height:20px; }
QFrame[frameShape="4"] { color:#3a3a5c; }
QLabel#headerTitle { color:#4CAF50; font-size:15px; font-weight:bold; }
QLabel#infoLabel { background:#1a3a1a; padding:6px 8px; border-radius:4px; color:#a5d6a7; }
QLabel#warnLabel { background:#3a2a00; padding:6px 8px; border-radius:4px; color:#ffcc80; }
"""

LIGHT_STYLE = """
QWidget { background-color:#f5f5f5; color:#212121;
  font-family:"Yu Gothic UI","Noto Sans JP","Meiryo UI",sans-serif; }
QMainWindow, QDialog { background-color:#f5f5f5; }
QGroupBox { border:1px solid #bdbdbd; border-radius:6px; margin-top:8px;
  padding-top:8px; color:#616161; font-weight:bold; }
QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 4px; }
QPushButton { background-color:#ffffff; color:#212121; border:1px solid #bdbdbd;
  border-radius:5px; padding:5px 12px; min-height:22px; }
QPushButton:hover { background-color:#e8f5e9; border-color:#4CAF50; }
QPushButton:disabled { background-color:#eeeeee; color:#9e9e9e; border-color:#e0e0e0; }
QPushButton#runButton { background-color:#4CAF50; color:#fff; border:1px solid #388E3C;
  font-weight:bold; font-size:13px; padding:8px 22px; }
QPushButton#runButton:hover { background-color:#388E3C; }
QPushButton#runButton:disabled { background-color:#a5d6a7; border-color:#81C784; }
QPushButton#stopButton { background-color:#ef5350; color:#fff; border:1px solid #c62828;
  font-weight:bold; font-size:13px; padding:8px 22px; }
QPushButton#stopButton:hover { background-color:#c62828; }
QComboBox { background-color:#fff; color:#212121; border:1px solid #bdbdbd;
  border-radius:4px; padding:4px 8px; min-height:22px; }
QComboBox QAbstractItemView { background-color:#fff; color:#212121;
  selection-background-color:#e8f5e9; border:1px solid #bdbdbd; }
QLineEdit, QSpinBox { background-color:#fff; color:#212121; border:1px solid #bdbdbd;
  border-radius:4px; padding:4px 8px; min-height:22px; }
QLineEdit:focus, QSpinBox:focus { border-color:#4CAF50; }
QLineEdit:read-only { background-color:#f0f0f0; color:#2e7d32; }
QTabWidget::pane { border:1px solid #bdbdbd; border-radius:4px; }
QTabBar::tab { background-color:#eeeeee; color:#616161; border:1px solid #bdbdbd; padding:6px 14px; }
QTabBar::tab:selected { background-color:#fff; color:#4CAF50; border-bottom:2px solid #4CAF50; }
QSlider::groove:horizontal { height:6px; background:#bdbdbd; border-radius:3px; }
QSlider::handle:horizontal { background:#4CAF50; width:16px; height:16px;
  margin:-5px 0; border-radius:8px; }
QSlider::sub-page:horizontal { background:#4CAF50; border-radius:3px; }
QCheckBox { color:#212121; spacing:6px; }
QCheckBox::indicator { width:16px; height:16px; border:1px solid #bdbdbd;
  border-radius:3px; background-color:#fff; }
QCheckBox::indicator:checked { background-color:#4CAF50; border-color:#4CAF50; }
QRadioButton { color:#212121; spacing:6px; }
QRadioButton::indicator { width:14px; height:14px; border:1px solid #bdbdbd;
  border-radius:7px; background-color:#fff; }
QRadioButton::indicator:checked { background-color:#4CAF50; border-color:#4CAF50; }
QTextEdit { background-color:#fafafa; color:#212121; border:1px solid #bdbdbd;
  border-radius:4px; font-family:"Consolas","Courier New",monospace; font-size:11px; }
QScrollBar:vertical { background:#f5f5f5; width:10px; border-radius:5px; }
QScrollBar::handle:vertical { background:#bdbdbd; border-radius:5px; min-height:20px; }
QLabel#headerTitle { color:#2e7d32; font-size:15px; font-weight:bold; }
QLabel#infoLabel { background:#e8f5e9; padding:6px 8px; border-radius:4px; color:#2e7d32; }
QLabel#warnLabel { background:#fff8e1; padding:6px 8px; border-radius:4px; color:#e65100; }
"""
