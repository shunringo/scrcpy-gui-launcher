# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for scrcpy GUI Launcher
# Build: pyinstaller scrcpy_gui_launcher.spec

block_cipher = None

a = Analysis(
    ['src/scrcpy_launcher.py'],
    pathex=['src'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt5.QtWidgets',
        'PyQt5.QtGui',
        'PyQt5.QtCore',
        'PyQt5.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='scrcpy-gui-launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # ウィンドウアプリ（コンソール非表示）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
