# scrcpy GUI Launcher

🌐 [English](./README.en.md) | 日本語

scrcpy v4.0 の主要オプションを GUI で設定・起動できる Windows 向けランチャーです。  
コマンドライン操作なしで scrcpy を使えます。

## 動作環境

- Windows 10 / 11 (64bit)
- Python 3.10 以上
- [scrcpy v4.0](https://github.com/Genymobile/scrcpy)（別途用意）

## セットアップ

```
scrcpy-win64-v4.0/      ← scrcpy 本体フォルダ
├── scrcpy.exe
├── adb.exe
├── *.dll ...
└── scrcpy-gui-launcher/  ← このリポジトリをここに配置
    ├── launch_gui.bat
    ├── scrcpy_launcher.py
    └── requirements.txt
```

1. scrcpy の ZIP を展開する
2. `scrcpy-gui-launcher/` フォルダを scrcpy フォルダ内に配置する
3. `launch_gui.bat` をダブルクリック（初回は PyQt5 を自動インストール）

または手動でインストール：

```
pip install PyQt5
python scrcpy_launcher.py
```

## 機能

| 機能 | 説明 |
|---|---|
| デバイス検出 | `adb devices` でデバイスを自動検出・選択 |
| USB / Wi-Fi 接続 | Wi-Fi ペアリング（Android 11+）にも対応 |
| 表示設定 | 解像度・FPS・ビットレート・回転・背景色など |
| 仮想ディスプレイ | `--new-display` / `--flex-display`（v4.0 新機能）|
| カメラ | カメラ映像ミラーリング（v4.0 新機能）|
| 録画 | MP4 / MKV 録画、ミラーリング非表示モード |
| コマンドプレビュー | 設定内容をリアルタイムでコマンド表示・コピー |
| プリセット | よく使う設定を JSON で保存・呼び出し |
| テーマ | ダークモード / ライトモード 切替 |

## scrcpy アップデート時

新バージョンの scrcpy フォルダに `scrcpy-gui-launcher/` をコピーするだけです。  
`scrcpy.exe` は親フォルダ → 同フォルダの順に自動検索します。

## ライセンス

[MIT License](./LICENSE) © 2026 shunringo

## Credits

This application is a GUI launcher for [scrcpy](https://github.com/Genymobile/scrcpy)
by [Genymobile](https://github.com/Genymobile), licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

scrcpy itself is not modified by this project.
