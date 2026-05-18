# -*- coding: utf-8 -*-

import ast
from pathlib import Path


def test_left_panel_width_is_fixed():
    tree = ast.parse(Path("src/main_window.py").read_text(encoding="utf-8"))
    assert _has_call(tree, "setFixedWidth", 270)


def test_device_combo_uses_minimum_contents_length():
    tree = ast.parse(Path("src/ui_panels.py").read_text(encoding="utf-8"))
    assert _has_attr(tree, "AdjustToMinimumContentsLengthWithIcon")
    assert _has_call(tree, "setMinimumContentsLength", 18)


def _has_call(tree: ast.AST, method: str, value: int) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr != method or len(node.args) != 1:
                continue
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and arg.value == value:
                return True
    return False


def _has_attr(tree: ast.AST, attr: str) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == attr:
            return True
    return False
