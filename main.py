#!/usr/bin/env python3
"""
Jarvis Trader Ecosystem - Entry Point

The full application currently lives in the nested folder
`jarvis-trader-ecosystem/`. This launcher provides a clean
entry point from the repository root.

Usage:
    python main.py
    python main.py --check-only   # config validation only
"""

import os
import sys
import runpy


def run_config_check(root: str) -> int:
    check_script = os.path.join(root, "scripts", "check_config.py")
    if not os.path.isfile(check_script):
        print("WARNING: scripts/check_config.py not found; skipping pre-flight check.")
        return 0
    # Run check in-process by path
    ns = runpy.run_path(check_script, run_name="__not_main__")
    main_fn = ns.get("main")
    if callable(main_fn):
        return int(main_fn())
    return 0


def main() -> int:
    root = os.path.dirname(os.path.abspath(__file__))
    nested_dir = os.path.join(root, "jarvis-trader-ecosystem")
    nested_main = os.path.join(nested_dir, "main.py")

    check_only = "--check-only" in sys.argv

    code = run_config_check(root)
    if check_only:
        return code
    if code != 0:
        print("Pre-flight config check failed. Fix .env then retry.")
        print("Or run: python scripts/check_config.py")
        return code

    if not os.path.isfile(nested_main):
        print("ERROR: Could not find the application at jarvis-trader-ecosystem/main.py")
        return 1

    if nested_dir not in sys.path:
        sys.path.insert(0, nested_dir)

    os.chdir(nested_dir)
    print("Starting Jarvis Trader Ecosystem...")
    print(f"Working directory: {os.getcwd()}")
    print("-" * 50)
    runpy.run_path(nested_main, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
