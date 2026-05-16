# scrcpy GUI Launcher

🌐 English | [日本語](./README.md)

A Windows GUI launcher for scrcpy v4.0.  
Configure and launch scrcpy without touching the command line.

## Requirements

- Windows 10 / 11 (64-bit)
- Python 3.10 or later
- [scrcpy v4.0](https://github.com/Genymobile/scrcpy) (obtained separately)

## Setup

```
scrcpy-win64-v4.0/      ← scrcpy installation folder
├── scrcpy.exe
├── adb.exe
├── *.dll ...
└── launcher/           ← place this repository here
    ├── launch_gui.bat
    ├── scrcpy_launcher.py
    └── requirements.txt
```

1. Extract the scrcpy ZIP archive.
2. Place the `launcher/` folder inside the scrcpy folder.
3. Double-click `launch_gui.bat` (PyQt5 is installed automatically on first run).

Or install manually:

```
pip install PyQt5
python scrcpy_launcher.py
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

Just copy the `launcher/` folder into the new scrcpy folder.  
`scrcpy.exe` is located automatically (parent folder first, then same folder).

## License

[MIT License](./LICENSE) © 2026 shunringo

## Credits

This application is a GUI launcher for [scrcpy](https://github.com/Genymobile/scrcpy)
by [Genymobile](https://github.com/Genymobile), licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

scrcpy itself is not modified by this project.
