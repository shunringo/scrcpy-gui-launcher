# scrcpy GUI Launcher

🌐 [English](./README.en.md) | 日本語

scrcpy v4.0 の主要オプションを GUI で設定・起動できる Windows 向けランチャーです。  
コマンドライン操作なしで scrcpy を使えます。

## 動作環境

- Windows 10 / 11 (64bit)
- [scrcpy v4.0](https://github.com/Genymobile/scrcpy)（別途用意）

## セットアップ

### 方法① EXE版（推奨・Python不要）

1. [scrcpy](https://github.com/Genymobile/scrcpy/releases) の ZIP を展開する
2. [Releases](https://github.com/shunringo/scrcpy-gui-launcher/releases/latest) から `scrcpy-gui-launcher.exe` をダウンロードする
3. `scrcpy-gui-launcher.exe` を scrcpy フォルダ内に配置する
4. `scrcpy-gui-launcher.exe` をダブルクリック

```
scrcpy-win64-v4.0/
├── scrcpy.exe
├── adb.exe
├── *.dll ...
└── scrcpy-gui-launcher.exe  ← ここに置くだけ
```

> ⚠️ Windows Defender が警告を出す場合は「詳細情報」→「実行」で起動できます。

### 方法② ソースから実行（開発者向け）

Python 3.10 以上が必要です。

```bash
git clone https://github.com/shunringo/scrcpy-gui-launcher.git
cd scrcpy-gui-launcher
pip install -r requirements.txt
python src/scrcpy_launcher.py
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

新バージョンの scrcpy フォルダに `scrcpy-gui-launcher.exe` をコピーするだけです。  
`scrcpy.exe` は同フォルダ内を自動検索します。

## ライセンス

[GNU General Public License v3.0](./LICENSE) © 2026 shunringo

## Credits

This application is a GUI launcher for [scrcpy](https://github.com/Genymobile/scrcpy)
by [Genymobile](https://github.com/Genymobile), licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

scrcpy itself is not modified by this project.
