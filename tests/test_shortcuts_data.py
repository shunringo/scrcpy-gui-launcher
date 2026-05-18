# -*- coding: utf-8 -*-

from shortcut_data import SHORTCUT_NOTES, SHORTCUT_SECTIONS, SHORTCUT_SOURCE_URL


def test_shortcut_source_url_points_to_official_doc():
    assert "github.com/Genymobile/scrcpy" in SHORTCUT_SOURCE_URL
    assert SHORTCUT_SOURCE_URL.endswith("doc/shortcuts.md")


def test_shortcut_sections_cover_keyboard_and_mouse():
    titles_ja = [section["title"]["ja"] for section in SHORTCUT_SECTIONS]
    assert "キーボードショートカット" in titles_ja
    assert "マウスショートカット" in titles_ja


def test_shortcut_sections_are_detailed():
    item_count = sum(len(section["items"]) for section in SHORTCUT_SECTIONS)
    assert item_count >= 40
    assert len(SHORTCUT_NOTES) >= 5
