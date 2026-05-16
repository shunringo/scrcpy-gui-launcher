# conftest.py — src/ を sys.path に追加して各テストファイルから import できるようにする
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
