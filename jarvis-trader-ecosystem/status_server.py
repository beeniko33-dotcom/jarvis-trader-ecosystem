#!/usr/bin/env python3
"""
Jarvis Trader status API + simple web dashboard.

Endpoints:
  GET /           HTML operations dashboard
  GET /health     {"status": "ok"}
  GET /status     summary metrics
  GET /signals    recent signal_history (limit via ?limit=20)
  GET /trades     paper trades (open + closed summary)

Run (from nested app dir, same place as jarvis_memory.json):

    python status_server.py

Env: STATUS_HOST (default 127.0.0.1), STATUS_PORT (8787), MEMORY_FILE
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

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


def build_signals(limit: int = 20) -> dict:
    mem = load_memory()
    hist = list(mem.get("signal_history") or [])
    hist = hist[-max(1, min(limit, 100)) :]
    hist.reverse()
    return {"ok": True, "count": len(hist), "signals": hist}


def build_trades() -> dict:
    mem = load_memory()
    trades = mem.get("paper_trades") or []
    open_t = [t for t in trades if not t.get("closed")]
    closed = [t for t in trades if t.get("closed")]
    return {
        "ok": True,
        "balance": float(mem.get("paper_balance", 1000.0)),
        "open": open_t,
        "closed": closed[-50:],
        "open_count": len(open_t),
        "closed_count": len(closed),
    }


def dashboard_html() -> bytes:
    s = build_status()
    pairs = ", ".join(s.get("active_forex_pairs") or []) or "—"
    auto = s.get("autopilot") or {}
    paper = s.get("paper") or {}
    fb = s.get("feedback") or {}
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Jarvis Ops Dashboard</title>
<style>
  :root {{ font-family: system-ui, sans-serif; color: #e8eeff; background: #0b1020; }}
  body {{ margin: 0; padding: 24px; max-width: 900px; }}
  h1 {{ letter-spacing: 2px; margin: 0 0 8px; }}
  .sub {{ color: #8b9bb8; margin-bottom: 20px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
  .card {{ background: #151c33; border: 1px solid #243056; border-radius: 12px; padding: 14px; }}
  .label {{ color: #8b9bb8; font-size: 12px; }}
  .value {{ font-size: 22px; font-weight: 700; margin-top: 4px; }}
  .warn {{ color: #f5c542; }}
  a {{ color: #7c9cff; }}
  pre {{ background: #12182b; padding: 12px; border-radius: 8px; overflow: auto; font-size: 12px; }}
  button {{ background: #3d5afe; color: #fff; border: 0; padding: 10px 14px; border-radius: 8px; cursor: pointer; }}
</style>
</head>
<body>
  <h1>JARVIS OPS</h1>
  <p class="sub">Paper trading only · refreshed from jarvis_memory.json</p>
  <div class="grid">
    <div class="card"><div class="label">Paper balance</div><div class="value">${paper.get('balance', 0):.2f}</div></div>
    <div class="card"><div class="label">Autopilot</div><div class="value">{'ON' if auto.get('enabled') else 'OFF'}</div><div class="label">{auto.get('mode')}/{auto.get('risk')}</div></div>
    <div class="card"><div class="label">Open / Closed</div><div class="value">{paper.get('open_trades', 0)} / {paper.get('closed_trades', 0)}</div></div>
    <div class="card"><div class="label">Closed PnL</div><div class="value">{paper.get('closed_pnl', 0)}</div></div>
    <div class="card"><div class="label">Monitoring</div><div class="value">{'yes' if s.get('monitoring') else 'no'}</div></div>
    <div class="card"><div class="label">Signals logged</div><div class="value">{s.get('signals_logged', 0)}</div></div>
  </div>
  <p class="sub" style="margin-top:16px">Pairs: {pairs}<br/>Feedback +{fb.get('positive', 0)} / -{fb.get('negative', 0)} · {s.get('timestamp')}</p>
  <p>
    <a href="/status">/status</a> ·
    <a href="/signals?limit=20">/signals</a> ·
    <a href="/trades">/trades</a> ·
    <a href="/health">/health</a>
  </p>
  <button onclick="location.reload()">Refresh</button>
  <p class="warn">Control remains on Telegram. This page is read-only.</p>
</body>
</html>"""
    return html.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, body: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)

        if path == "/":
            self._send_html(dashboard_html())
            return
        if path == "/health":
            self._send_json(200, {"status": "ok", "service": "jarvis-trader-status"})
            return
        if path == "/status":
            self._send_json(200, build_status())
            return
        if path == "/signals":
            try:
                limit = int((qs.get("limit") or ["20"])[0])
            except ValueError:
                limit = 20
            self._send_json(200, build_signals(limit))
            return
        if path == "/trades":
            self._send_json(200, build_trades())
            return
        self._send_json(
            404,
            {"error": "not_found", "paths": ["/", "/health", "/status", "/signals", "/trades"]},
        )


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Jarvis status + dashboard on http://{HOST}:{PORT}")
    print("  GET /  /health  /status  /signals  /trades")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
