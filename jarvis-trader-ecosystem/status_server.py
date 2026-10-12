#!/usr/bin/env python3
"""
Lightweight HTTP status API for Jarvis Trader.

Reads jarvis_memory.json written by the Telegram bot and serves:
  GET /health  -> {"status": "ok"}
  GET /status  -> paper balance, autopilot, open trades, pairs, etc.

Run alongside the bot (separate process):

    cd jarvis-trader-ecosystem
    python status_server.py

Default: http://127.0.0.1:8787
Env:
  STATUS_HOST=0.0.0.0
  STATUS_PORT=8787
  MEMORY_FILE=jarvis_memory.json
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = os.getenv("STATUS_HOST", "127.0.0.1")
PORT = int(os.getenv("STATUS_PORT", "8787"))
MEMORY_FILE = Path(os.getenv("MEMORY_FILE", "jarvis_memory.json"))
STARTED_AT = datetime.now(timezone.utc).isoformat()

_lock = threading.Lock()


def load_memory() -> dict:
    with _lock:
        if not MEMORY_FILE.is_file():
            return {}
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}


def build_status() -> dict:
    mem = load_memory()
    trades = mem.get("paper_trades") or []
    open_trades = [t for t in trades if not t.get("closed")]
    closed = [t for t in trades if t.get("closed")]
    total_pnl = sum(float(t.get("profit") or 0) for t in closed)

    return {
        "service": "jarvis-trader-status",
        "ok": True,
        "server_started_at": STARTED_AT,
        "memory_file": str(MEMORY_FILE.resolve()) if MEMORY_FILE.exists() else str(MEMORY_FILE),
        "memory_present": MEMORY_FILE.is_file(),
        "monitoring": bool(mem.get("monitoring", False)),
        "autopilot": {
            "enabled": bool(mem.get("autopilot_enabled", False)),
            "mode": mem.get("autopilot_mode", "balanced"),
            "risk": mem.get("autopilot_risk", "medium"),
        },
        "alert_threshold": mem.get("alert_threshold", 75),
        "scan_interval_min": mem.get("scan_interval_min", 5),
        "active_forex_pairs": mem.get("active_forex_pairs") or [],
        "paper": {
            "balance": float(mem.get("paper_balance", 1000.0)),
            "open_trades": len(open_trades),
            "closed_trades": len(closed),
            "closed_pnl": round(total_pnl, 4),
        },
        "signals_logged": len(mem.get("signal_history") or []),
        "feedback": {
            "positive": int(mem.get("feedback_positive") or 0),
            "negative": int(mem.get("feedback_negative") or 0),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        # Quieter logs
        return

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/health":
            self._send(200, {"status": "ok", "service": "jarvis-trader-status"})
            return
        if path == "/status":
            self._send(200, build_status())
            return
        self._send(404, {"error": "not_found", "paths": ["/health", "/status"]})


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Jarvis status server on http://{HOST}:{PORT}")
    print("  GET /health")
    print("  GET /status")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down status server")
        server.shutdown()


if __name__ == "__main__":
    main()
