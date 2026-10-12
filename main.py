#!/usr/bin/env python3
"""
Jarvis Trader Ecosystem - Entry Point

The full application currently lives in the nested folder
`jarvis-trader-ecosystem/`. This launcher provides a clean
entry point from the repository root.

Usage:
    python main.py
"""

import os
import sys
import runpy

def main():
    nested_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis-trader-ecosystem")
    nested_main = os.path.join(nested_dir, "main.py")

    if not os.path.isfile(nested_main):
        print("ERROR: Could not find the application at jarvis-trader-ecosystem/main.py")
        print("Please ensure the nested application folder is present.")
        sys.exit(1)

    # Make the nested package importable
    if nested_dir not in sys.path:
        sys.path.insert(0, nested_dir)

    # Change working directory so relative paths (memory file, models, .env) resolve correctly
    os.chdir(nested_dir)

    print("Starting Jarvis Trader Ecosystem...")
    print(f"Working directory: {os.getcwd()}")
    print("-" * 50)

    # Execute the real application
    runpy.run_path(nested_main, run_name="__main__")

if __name__ == "__main__":
    main()
