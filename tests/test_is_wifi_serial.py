# -*- coding: utf-8 -*-
"""Tests for _is_wifi_serial() in main_window.py"""

import sys
import types
import pytest

# ── import _is_wifi_serial without triggering PyQt5 GUI ───────────────────
# We import only the helper function by extracting it from the module source
# so this test file can run even in headless environments where PyQt5
# widgets cannot be instantiated.

import importlib, ast, textwrap

def _load_is_wifi_serial():
    """Read main_window.py, extract _is_wifi_serial, execute it in isolation."""
    from pathlib import Path
    src_path = Path(__file__).parent.parent / "src" / "main_window.py"
    src = src_path.read_text(encoding="utf-8")

    # Extract just the function definition (no PyQt5 imports needed)
    import re
    m = re.search(
        r"(def _is_wifi_serial\(.*?)\n(?=\n[^\s])",
        src,
        re.DOTALL,
    )
    assert m, "_is_wifi_serial not found in main_window.py"
    func_src = textwrap.dedent(m.group(1))

    import re as _re
    ns: dict = {"re": _re}
    exec(compile(func_src, "<_is_wifi_serial>", "exec"), ns)  # noqa: S102
    return ns["_is_wifi_serial"]


_is_wifi_serial = _load_is_wifi_serial()


# ── Wi-Fi serials (should return True) ───────────────────────────────────

@pytest.mark.parametrize("serial", [
    "192.168.1.10:5555",
    "10.0.0.1:5555",
    "172.16.0.5:43210",
    "192.168.0.100:5555",
    "127.0.0.1:5555",
    "adb-12345678._adb-tls-connect._tcp",
    "adb-ABCDEF01._adb-tls-connect._tcp",
    "adb-00001234._adb-tls-connect._tcp.local",
    "hostname:1234",
    "some-host.local:5555",
])
def test_wifi_serial_returns_true(serial):
    assert _is_wifi_serial(serial) is True, f"Expected True for: {serial!r}"


# ── USB / unknown serials (should return False) ───────────────────────────

@pytest.mark.parametrize("serial", [
    "emulator-5554",
    "ZY3224S2GX",
    "RF8N10ABCDE",
    "192.168.1.10",           # IP without port — not a serial
    "localhost",
    "R58M84XWXXX",
    "0123456789ABCDEF",
    "device",
    "",
])
def test_usb_serial_returns_false(serial):
    assert _is_wifi_serial(serial) is False, f"Expected False for: {serial!r}"


# ── edge cases ────────────────────────────────────────────────────────────

def test_ip_colon_zero_port_is_wifi():
    """host:0 is technically valid host:port format."""
    assert _is_wifi_serial("192.168.1.1:0") is True

def test_ip_colon_large_port_is_wifi():
    assert _is_wifi_serial("10.0.0.1:65535") is True

def test_mdns_substring_only_detected_correctly():
    """Only exact substring triggers mDNS detection."""
    assert _is_wifi_serial("adb-1234._adb-tls-connect._tcp") is True
    assert _is_wifi_serial("adb-1234._adb-tls-other._tcp") is False

def test_returns_bool():
    assert isinstance(_is_wifi_serial("emulator-5554"), bool)
    assert isinstance(_is_wifi_serial("192.168.1.1:5555"), bool)
