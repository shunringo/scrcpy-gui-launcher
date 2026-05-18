# -*- coding: utf-8 -*-

from pathlib import Path


def test_left_panel_width_is_fixed():
    text = Path("src/main_window.py").read_text(encoding="utf-8")
    assert "setFixedWidth(270)" in text


def test_device_combo_uses_minimum_contents_length():
    text = Path("src/ui_panels.py").read_text(encoding="utf-8")
    assert "AdjustToMinimumContentsLengthWithIcon" in text
    assert "setMinimumContentsLength(18)" in text
