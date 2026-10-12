#!/usr/bin/env python3
"""
Smoke tests that do not require Telegram credentials.

Run:
    python tests/test_smoke.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_launcher_parses() -> None:
    src = (ROOT / "main.py").read_text(encoding="utf-8")
    ast.parse(src)


def test_nested_main_parses() -> None:
    path = ROOT / "jarvis-trader-ecosystem" / "main.py"
    assert path.is_file(), "nested main.py missing"
    ast.parse(path.read_text(encoding="utf-8"))


def test_predictor_parses() -> None:
    path = ROOT / "jarvis-trader-ecosystem" / "models" / "predictor.py"
    assert path.is_file(), "predictor.py missing"
    ast.parse(path.read_text(encoding="utf-8"))


def test_check_config_parses() -> None:
    path = ROOT / "scripts" / "check_config.py"
    assert path.is_file()
    ast.parse(path.read_text(encoding="utf-8"))


def test_public_forex_api() -> None:
    try:
        import requests
    except ImportError:
        print("skip forex api (requests not installed)")
        return
    r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=15)
    assert r.status_code == 200, r.status_code
    data = r.json()
    assert "rates" in data and "EUR" in data["rates"]


def main() -> int:
    tests = [
        test_launcher_parses,
        test_nested_main_parses,
        test_predictor_parses,
        test_check_config_parses,
        test_public_forex_api,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print("-" * 40)
    if failed:
        print(f"{failed} test(s) failed")
        return 1
    print("All smoke tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
