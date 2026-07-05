import os, sys, asyncio, logging, json, time, subprocess
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# ----- Self-update restarter -----
def restart_bot():
    """Replace the current process with a fresh instance of this script."""
    logger.info("♻️ Restarting bot...")
    os.execv(sys.executable, [sys.executable, __file__])

# ----- Setup -----
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BINANCE_API = "https://api.binance.com/api/v3"

# ========== AI OVERSEER CONTROLLER ==========
class JarvisController:
    def __init__(self):
        self.monitoring = True
        self.active_symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        self.scan_interval = 1800
        self.alert_threshold = 75
        self.last_signals = {}

    def toggle_monitoring(self, state: bool):
        self.monitoring = state
        return self.monitoring

    def set_symbols(self, symbols):
        self.active_symbols = [s.upper() for s in symbols]
        return self.active_symbols

    def adjust_interval(self, minutes: int):
        self.scan_interval = max(60, minutes * 60)
        return self.scan_interval

    def get_status_report(self):
        return {
            "monitoring": self.monitoring,
            "symbols": self.active_symbols,
            "scan_interval_min": self.scan_interval // 60,
            "last_signals": self.last_signals,
        }

controller = JarvisController()

# ----- Data fetching -----
def fetch_klines(symbol="BTCUSDT", interval="1h", limit=100):
    url = f"{BINANCE_API}/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    if isinstance(data, dict) and "code" in data:
        raise Exception(data.get("msg", "Binance error"))
    candles = []
    for entry in data:
        candles.append({
            "time": int(entry[0]),
            "open": float(entry[1]),
            "high": float(entry[2]),
            "low": float(entry[3]),
            "close": float(entry[4]),
            "volume": float(entry[5]),
        })
    return candles

# ----- Indicators (pure Python) -----
def compute_rsi(candles, period=14):
    if len(candles) < period + 1:
        return None
    closes = [c["close"] for c in candles]
    gains = [max(closes[i] - closes[i-1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i-1] - closes[i], 0) for i in range(1, len(closes))]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 1)

def detect_patterns(candles):
    if len(candles) < 26:
        return []
    closes = [c["close"] for c in candles]
    ema12 = sum(closes[-12:]) / 12
    ema26 = sum(closes[-26:]) / 26
    macd = ema12 - ema26
    signal = sum(closes[-9:]) / 9
    prev_ema12 = sum(closes[-13:-1]) / 12
    prev_ema26 = sum(closes[-27:-1]) / 26
    prev_macd = prev_ema12 - prev_ema26
    prev_signal = sum(closes[-10:-1]) / 9
    alerts = []
    if prev_macd < prev_signal and macd > signal:
        alerts.append({"name": "MACD Bullish Cross", "confidence": 85})
    elif prev_macd > prev_signal and macd < signal:
        alerts.append({"name": "MACD Bearish Cross", "confidence": 85})
    change = (closes[-1] - closes[0]) / closes[0] * 100
    if abs(change) > 2:
        alerts.append({"name": f"Strong {'up' if change>0 else 'down'}trend", "confidence": 80})
    rsi = compute_rsi(candles, 14)
    if rsi and rsi < 30:
        alerts.append({"name": "RSI Oversold", "confidence": 75})
    elif rsi and rsi > 70:
        alerts.append({"name": "RSI Overbought", "confidence": 75})
    return alerts

# ----- Background scan -----
async def master_scan(context: ContextTypes.DEFAULT_TYPE):
    if not controller.monitoring:
        return
    for symbol in controller.active_symbols:
        try:
            candles = fetch_klines(symbol, "1h", 200)
            patterns = detect_patterns(candles)
            controller.last_signals[symbol] = patterns
            for p in patterns:
                if p["confidence"] >= controller.alert_threshold:
                    await context.bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"🤖 *Jarvis AI Alert* – {symbol}\n{p['name']} (confidence: {p['confidence']}%)",
                        parse_mode="Markdown"
                    )
        except Exception as e:
            logger.warning(f"Scan failed for {symbol}: {e}")

# ========== COMMANDS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Jarvis AI Overseer Online*\n\n"
        "Commands:\n"
        "/scan – quick scan\n"
        "/rsi – RSI check\n"
        "/status – system overview\n"
        "/monitor on|off – background monitoring\n"
        "/symbols BTC ETH – set tracked symbols\n"
        "/interval <minutes> – scan interval\n"
        "/oversee – full AI market report\n"
        "/update – pull latest code from GitHub & restart\n"
        "/restart – restart the bot (no git pull)",
        parse_mode="Markdown"
    )

async def scan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Running overseer scan...")
    await master_scan(context)
    await update.message.reply_text("✅ Scan complete.")

async def rsi_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = ""
    for sym in controller.active_symbols:
        candles = fetch_klines(sym, "1h", 100)
        rsi = compute_rsi(candles)
        msg += f"{sym} RSI: {rsi if rsi else 'N/A'}\n"
    await update.message.reply_text(msg or "No data.")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    report = controller.get_status_report()
    text = (
        f"*Jarvis AI Status*\n"
        f"Monitoring: {'ON' if report['monitoring'] else 'OFF'}\n"
        f"Symbols: {', '.join(report['symbols'])}\n"
        f"Scan interval: {report['scan_interval_min']} min"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def monitor_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0].lower() == "on":
        controller.toggle_monitoring(True)
        await update.message.reply_text("✅ Monitoring ON.")
    elif context.args and context.args[0].lower() == "off":
        controller.toggle_monitoring(False)
        await update.message.reply_text("⏸️ Monitoring OFF.")
    else:
        await update.message.reply_text("Usage: /monitor on|off")

async def symbols_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /symbols BTC ETH SOL ...")
        return
    new_syms = controller.set_symbols(context.args)
    await update.message.reply_text(f"✅ Symbols: {', '.join(new_syms)}")

async def interval_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /interval 10")
        return
    try:
        mins = int(context.args[0])
        new_int = controller.adjust_interval(mins)
        await update.message.reply_text(f"✅ Interval set to {new_int//60} min.")
    except:
        await update.message.reply_text("Invalid number.")

async def oversee_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Analyzing all markets...")
    report_lines = ["*🧠 Jarvis AI Market Report*"]
    for sym in controller.active_symbols:
        candles = fetch_klines(sym, "1h", 200)
        patterns = detect_patterns(candles)
        rsi = compute_rsi(candles)
        change = (candles[-1]["close"] - candles[0]["close"]) / candles[0]["close"] * 100 if candles else 0
        report_lines.append(
            f"\n*{sym}* | 1h change: {change:+.2f}% | RSI: {rsi if rsi else 'N/A'}\n"
            + ("No patterns" if not patterns else "\n".join([f"• {p['name']} ({p['confidence']}%)" for p in patterns]))
        )
    await update.message.reply_text("\n".join(report_lines), parse_mode="Markdown")

async def update_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pull latest code from GitHub and restart."""
    await update.message.reply_text("🔄 Pulling latest code from GitHub...")
    try:
        result = subprocess.run(
            ["git", "pull"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            await update.message.reply_text(f"❌ Git pull failed:\n{result.stderr}")
            return
        await update.message.reply_text("✅ Code updated. Restarting...")
        time.sleep(1)
        restart_bot()
    except Exception as e:
        await update.message.reply_text(f"❌ Error during update: {e}")

async def restart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("♻️ Restarting bot...")
    time.sleep(1)
    restart_bot()

# ========== MAIN ==========
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan_cmd))
    app.add_handler(CommandHandler("rsi", rsi_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("monitor", monitor_cmd))
    app.add_handler(CommandHandler("symbols", symbols_cmd))
    app.add_handler(CommandHandler("interval", interval_cmd))
    app.add_handler(CommandHandler("oversee", oversee_cmd))
    app.add_handler(CommandHandler("update", update_cmd))
    app.add_handler(CommandHandler("restart", restart_cmd))
    app.job_queue.run_repeating(master_scan, interval=300, first=10)
    logger.info("🤖 Self-upgrading Jarvis AI Overseer started...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
