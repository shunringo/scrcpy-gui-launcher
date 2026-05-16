# scrcpy GUI Launcher

🌐 English | [日本語](./README.md)

A Windows GUI launcher for scrcpy v4.0.  
Configure and launch scrcpy without touching the command line.

## Requirements

- Windows 10 / 11 (64-bit)
- [scrcpy v4.0](https://github.com/Genymobile/scrcpy) (obtained separately)

## Setup

### Option ① EXE release (recommended — no Python required)

1. Download and extract [scrcpy](https://github.com/Genymobile/scrcpy/releases).
2. Download `scrcpy-gui-launcher.exe` from [Releases](https://github.com/shunringo/scrcpy-gui-launcher/releases/latest).
3. Place `scrcpy-gui-launcher.exe` inside the scrcpy folder.
4. Double-click `scrcpy-gui-launcher.exe`.

```
scrcpy-win64-v4.0/
├── scrcpy.exe
├── adb.exe
├── *.dll ...
└── scrcpy-gui-launcher.exe  ← just place it here
```

> ⚠️ If Windows Defender shows a warning, click "More info" → "Run anyway".

### Option ② Run from source (for developers)

Python 3.10 or later is required.

```bash
git clone https://github.com/shunringo/scrcpy-gui-launcher.git
cd scrcpy-gui-launcher
pip install -r requirements.txt
python src/scrcpy_launcher.py
```

## Features

| Feature | Description |
|---|---|
| Device detection | Auto-detect and select devices via `adb devices` |
| USB / Wi-Fi connection | Supports Wi-Fi pairing (Android 11+) |
| Display settings | Resolution, FPS, bitrate, rotation, background color, etc. |
| Virtual display | `--new-display` / `--flex-display` (new in v4.0) |
| Camera | Camera video mirroring (new in v4.0) |
| Recording | MP4 / MKV recording with optional no-display mode |
| Command preview | Real-time command preview with one-click copy |
| Presets | Save and recall your favourite settings as JSON |
| Theme | Dark mode / Light mode toggle |
| Language | Japanese / English UI (switchable at runtime) |

## Updating scrcpy

Just copy `scrcpy-gui-launcher.exe` into the new scrcpy folder.  
`scrcpy.exe` is located automatically in the same folder.

## License

[GNU General Public License v3.0](./LICENSE) © 2026 shunringo

## Credits

This application is a GUI launcher for [scrcpy](https://github.com/Genymobile/scrcpy)
by [Genymobile](https://github.com/Genymobile), licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

scrcpy itself is not modified by this project.
