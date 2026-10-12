#!/usr/bin/env python3
"""
Simple configuration check for Jarvis Trader Ecosystem.
Run from repository root before starting the bot:

    python scripts/check_config.py
"""

import os
import sys
from pathlib import Path

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    nested = root / "jarvis-trader-ecosystem"

    print("Jarvis config check")
    print("=" * 40)

    # Look for .env in root and nested
    env_candidates = [root / ".env", nested / ".env"]
    found_env = [p for p in env_candidates if p.is_file()]

    if not found_env:
        print("[!] No .env file found.")
        print("    Copy .env.example to .env and fill TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID.")
        return 1

    for p in found_env:
        print(f"[+] Found env file: {p}")

    # Load the first found .env manually (avoid requiring dotenv just for the check)
    token = None
    chat_id = None
    for p in found_env:
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN") and val and "your_" not in val.lower():
                token = val
            if key in ("TELEGRAM_CHAT_ID",) and val and "your_" not in val.lower():
                chat_id = val

    if not token:
        print("[!] TELEGRAM_BOT_TOKEN (or TELEGRAM_TOKEN) missing or still a placeholder.")
        return 1
    print("[+] Telegram bot token looks set.")

    if not chat_id:
        print("[!] TELEGRAM_CHAT_ID missing or still a placeholder.")
        print("    The bot may still discover chat id on first message, but set it if known.")
    else:
        print("[+] TELEGRAM_CHAT_ID looks set.")

    if not (nested / "main.py").is_file():
        print("[!] Nested application main.py not found.")
        return 1
    print("[+] Nested application present.")

    print("=" * 40)
    print("Config check passed (basic). You can run: python main.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())
