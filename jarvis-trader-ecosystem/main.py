import os, sys, asyncio, logging, json, time, random, subprocess, math
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# ===== Self-update restarter =====
def restart_bot():
    logger.info("♻️ Restarting bot...")
    os.execv(sys.executable, [sys.executable, __file__])

# ===== Setup =====
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BINANCE_API = "https://api.binance.com/api/v3"
FEAR_GREED_URL = "https://api.alternative.me/fng/?limit=1"

# ===== AI Memory & Evolution =====
MEMORY_FILE = "jarvis_memory.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE) as f:
            return json.load(f)
    return {
        "alert_threshold": 75,
        "monitoring": True,
        "active_symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        "scan_interval_min": 5,
        "signal_history": [],
        "feedback_positive": 0,
        "feedback_negative": 0,
        "interaction_count": 0,
        "last_evolved": None
    }

def save_memory(mem):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(mem, f, indent=2)

memory = load_memory()

class JarvisController:
    def __init__(self):
        self.memory = memory

    def toggle_monitoring(self, state: bool = None):
        if state is not None:
            self.memory["monitoring"] = state
        else:
            self.memory["monitoring"] = not self.memory["monitoring"]
        save_memory(self.memory)
        return self.memory["monitoring"]

    def set_symbols(self, symbols):
        self.memory["active_symbols"] = [s.upper() for s in symbols]
        save_memory(self.memory)
        return self.memory["active_symbols"]

    def add_symbol(self, sym):
        if sym.upper() not in self.memory["active_symbols"]:
            self.memory["active_symbols"].append(sym.upper())
            save_memory(self.memory)
        return self.memory["active_symbols"]

    def remove_symbol(self, sym):
        if sym.upper() in self.memory["active_symbols"]:
            self.memory["active_symbols"].remove(sym.upper())
            save_memory(self.memory)
        return self.memory["active_symbols"]

    def set_threshold(self, val):
        self.memory["alert_threshold"] = max(50, min(100, val))
        save_memory(self.memory)
        return self.memory["alert_threshold"]

    def adjust_interval(self, minutes):
        self.memory["scan_interval_min"] = max(1, minutes)
        save_memory(self.memory)
        return self.memory["scan_interval_min"]

    def log_signal(self, signal):
        self.memory["signal_history"].append({
            "time": datetime.now().isoformat(),
            **signal
        })
        save_memory(self.memory)

    def add_feedback(self, positive):
        if positive:
            self.memory["feedback_positive"] += 1
        else:
            self.memory["feedback_negative"] += 1
        # Auto-evolve threshold based on feedback
        if self.memory["feedback_negative"] > self.memory["feedback_positive"] and self.memory["alert_threshold"] < 95:
            self.memory["alert_threshold"] += 1
        elif self.memory["feedback_positive"] > self.memory["feedback_negative"] and self.memory["alert_threshold"] > 50:
            self.memory["alert_threshold"] -= 1
        save_memory(self.memory)

    def evolve(self):
        # Analyze signal history and adjust parameters
        if len(self.memory["signal_history"]) < 5:
            return "Not enough data to evolve yet."
        self.memory["last_evolved"] = datetime.now().isoformat()
        save_memory(self.memory)
        # Example: if many false signals, increase threshold
        if self.memory["feedback_negative"] > self.memory["feedback_positive"]:
            self.set_threshold(self.memory["alert_threshold"] + 2)
            return f"🔧 Threshold increased to {self.memory['alert_threshold']}% (more selective)."
        else:
            return "✅ Parameters already balanced. No evolution needed."

    def get_status(self):
        return {
            **self.memory,
            "last_signals": self.memory["signal_history"][-5:]
        }

controller = JarvisController()

# ===== Data fetching (pure Python) =====
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

def fetch_ticker(symbol):
    url = f"{BINANCE_API}/ticker/24hr"
    resp = requests.get(url, params={"symbol": symbol}, timeout=10)
    return resp.json()

# ===== Indicators (pure Python) =====
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

def detect_bull_bear(candles):
    if len(candles) < 20:
        return "neutral"
    closes = [c["close"] for c in candles]
    ma20 = sum(closes[-20:]) / 20
    if closes[-1] > ma20 * 1.02:
        return "bullish"
    elif closes[-1] < ma20 * 0.98:
        return "bearish"
    return "neutral"

def simple_backtest(candles, fast=10, slow=30):
    if len(candles) < slow:
        return "Insufficient data"
    closes = [c["close"] for c in candles]
    capital = 1000
    position = 0
    for i in range(slow, len(closes)):
        ma_fast = sum(closes[i-fast:i]) / fast
        ma_slow = sum(closes[i-slow:i]) / slow
        prev_ma_fast = sum(closes[i-fast-1:i-1]) / fast
        prev_ma_slow = sum(closes[i-slow-1:i-1]) / slow
        if prev_ma_fast < prev_ma_slow and ma_fast > ma_slow and position == 0:
            position = capital / closes[i]
            capital = 0
        elif prev_ma_fast > prev_ma_slow and ma_fast < ma_slow and position > 0:
            capital = position * closes[i]
            position = 0
    final = capital + (position * closes[-1] if position else 0)
    profit = final - 1000
    return f"Backtest MA{fast}/{slow} crossover: initial $1000 → ${final:.2f} ({profit:+.2f}%)"

def get_fear_greed():
    try:
        data = requests.get(FEAR_GREED_URL, timeout=5).json()
        val = int(data["data"][0]["value"])
        classification = data["data"][0]["value_classification"]
        return val, classification
    except:
        return None, None

def get_top_movers():
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "DOGEUSDT", "XRPUSDT", "BNBUSDT"]
    movers = []
    for sym in symbols:
        try:
            t = fetch_ticker(sym)
            change = float(t.get("priceChangePercent", 0))
            movers.append((sym, change))
        except:
            pass
    movers.sort(key=lambda x: abs(x[1]), reverse=True)
    return movers[:5]

# ===== Telegram Command Handlers (1000+ commands spirit) =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Jarvis AI Overseer* ready, sir.\n\n"
        "I am your personal trading intelligence, capable of market scanning, RSI/MACD analysis, "
        "self‑evolution, backtesting, sentiment tracking, and more.\n\n"
        "Use /help for full command list.",
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📚 *Command Center*\n\n"
        "📊 *Market Analysis:*\n"
        "/scan – quick market scan\n"
        "/rsi – RSI values\n"
        "/oversee – full AI report\n"
        "/topmovers – top 24h movers\n"
        "/sentiment – Fear & Greed index\n"
        "/backtest – MA crossover backtest\n"
        "/predict <symbol> – short‑term prediction\n\n"
        "🧠 *AI Control:*\n"
        "/monitor on|off – background scanning\n"
        "/symbols <list> – set tracked symbols\n"
        "/addsymbol <sym> / removesymbol <sym>\n"
        "/interval <min> – scan interval\n"
        "/setthreshold <value> – alert confidence threshold\n"
        "/feedback good|bad – train the AI\n"
        "/evolve – auto‑optimize parameters\n"
        "/logs – recent activity\n"
        "/alerts – recent signals\n"
        "/status – system overview\n\n"
        "🔄 *System:*\n"
        "/update – pull from GitHub & restart\n"
        "/restart – soft restart\n"
        "/ping – check if alive"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Online, sir.")

async def scan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Scanning markets...")
    for sym in controller.memory["active_symbols"]:
        candles = fetch_klines(sym, "1h", 200)
        patterns = detect_patterns(candles)
        if patterns:
            for p in patterns:
                if p["confidence"] >= controller.memory["alert_threshold"]:
                    await update.message.reply_text(f"⚠️ {sym}: {p['name']} ({p['confidence']}%)", parse_mode="Markdown")
    await update.message.reply_text("✅ Scan complete.")

async def rsi_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = ""
    for sym in controller.memory["active_symbols"]:
        candles = fetch_klines(sym, "1h", 100)
        rsi = compute_rsi(candles)
        msg += f"{sym} RSI: {rsi if rsi else 'N/A'}\n"
    await update.message.reply_text(msg or "No data.")

async def oversee_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Jarvis is analyzing all markets...")
    report = ["*Jarvis AI Market Report*"]
    for sym in controller.memory["active_symbols"]:
        candles = fetch_klines(sym, "1h", 200)
        patterns = detect_patterns(candles)
        rsi = compute_rsi(candles)
        change = (candles[-1]["close"] - candles[0]["close"]) / candles[0]["close"] * 100 if candles else 0
        bias = detect_bull_bear(candles)
        report.append(f"\n*{sym}* | {change:+.2f}% | RSI: {rsi if rsi else 'N/A'} | Bias: {bias}")
        for p in patterns:
            report.append(f"• {p['name']} ({p['confidence']}%)")
    await update.message.reply_text("\n".join(report), parse_mode="Markdown")

async def topmovers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movers = get_top_movers()
    msg = "📈 *Top 24h Movers*\n" + "\n".join([f"{'🟢' if ch>=0 else '🔴'} {s}: {ch:+.2f}%" for s,ch in movers])
    await update.message.reply_text(msg, parse_mode="Markdown")

async def sentiment_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val, cls = get_fear_greed()
    if val:
        emoji = "😱" if val < 30 else "😐" if val < 60 else "😀"
        await update.message.reply_text(f"Crypto Fear & Greed Index: *{val}* – {cls} {emoji}", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Could not fetch sentiment data.")

async def backtest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    candles = fetch_klines("BTCUSDT", "1h", 500)
    result = simple_backtest(candles)
    await update.message.reply_text(result)

async def predict_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sym = context.args[0].upper() if context.args else "BTCUSDT"
    candles = fetch_klines(sym, "1h", 100)
    rsi = compute_rsi(candles)
    bias = detect_bull_bear(candles)
    if rsi and rsi < 30:
        prediction = "🟢 Likely to bounce (oversold)."
    elif rsi and rsi > 70:
        prediction = "🔴 Likely to pull back (overbought)."
    else:
        prediction = "⚪ Neutral."
    await update.message.reply_text(f"*Prediction for {sym}:* {prediction}\nBias: {bias}", parse_mode="Markdown")

async def monitor_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        state = context.args[0].lower()
        if state in ["on", "true", "1"]:
            controller.toggle_monitoring(True)
            await update.message.reply_text("✅ Monitoring ON.")
        elif state in ["off", "false", "0"]:
            controller.toggle_monitoring(False)
            await update.message.reply_text("⏸️ Monitoring OFF.")
        else:
            await update.message.reply_text("Usage: /monitor on|off")
    else:
        status = controller.toggle_monitoring()
        await update.message.reply_text(f"Monitoring {'ON' if status else 'OFF'}.")

async def symbols_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /symbols BTC ETH SOL ...")
        return
    syms = controller.set_symbols(context.args)
    await update.message.reply_text(f"✅ Tracking: {', '.join(syms)}")

async def addsymbol_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /addsymbol ADA")
        return
    syms = controller.add_symbol(context.args[0])
    await update.message.reply_text(f"✅ Added. Now: {', '.join(syms)}")

async def removesymbol_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /removesymbol ADA")
        return
    syms = controller.remove_symbol(context.args[0])
    await update.message.reply_text(f"✅ Removed. Now: {', '.join(syms)}")

async def interval_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /interval 10 (minutes)")
        return
    try:
        mins = int(context.args[0])
        controller.adjust_interval(mins)
        await update.message.reply_text(f"✅ Scan interval set to {mins} min.")
    except:
        await update.message.reply_text("Invalid number.")

async def setthreshold_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /setthreshold 75")
        return
    try:
        val = int(context.args[0])
        controller.set_threshold(val)
        await update.message.reply_text(f"✅ Alert threshold set to {val}%")
    except:
        await update.message.reply_text("Invalid number.")

async def feedback_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or context.args[0].lower() not in ["good", "bad"]:
        await update.message.reply_text("Usage: /feedback good|bad")
        return
    is_good = context.args[0].lower() == "good"
    controller.add_feedback(is_good)
    await update.message.reply_text(f"📝 Feedback recorded as {'positive' if is_good else 'negative'}. Thank you, sir.")

async def evolve_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = controller.evolve()
    await update.message.reply_text(f"🧬 {result}")

async def alerts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history = controller.memory["signal_history"][-10:]
    if not history:
        await update.message.reply_text("No recent alerts.")
    else:
        lines = ["*Recent Alerts*"]
        for h in reversed(history):
            lines.append(f"• {h['time'][:16]} – {h.get('name','Signal')} ({h.get('confidence','?')}%)")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def logs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(MEMORY_FILE) as f:
        data = json.load(f)
    # simple stats
    total_signals = len(data["signal_history"])
    pos_fb = data["feedback_positive"]
    neg_fb = data["feedback_negative"]
    await update.message.reply_text(
        f"📋 *Jarvis Logs*\nTotal signals: {total_signals}\nPositive feedback: {pos_fb}\nNegative feedback: {neg_fb}\nThreshold: {data['alert_threshold']}%\nMonitoring: {'ON' if data['monitoring'] else 'OFF'}",
        parse_mode="Markdown"
    )

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mem = controller.memory
    text = (
        f"*Jarvis Status*\n"
        f"Monitoring: {'ON' if mem['monitoring'] else 'OFF'}\n"
        f"Symbols: {', '.join(mem['active_symbols'])}\n"
        f"Scan interval: {mem['scan_interval_min']} min\n"
        f"Alert threshold: {mem['alert_threshold']}%\n"
        f"Signals: {len(mem['signal_history'])}\n"
        f"Feedback: +{mem['feedback_positive']} / -{mem['feedback_negative']}\n"
        f"Last evolved: {mem.get('last_evolved','never')}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def update_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# ===== Background Master Scan =====
async def master_scan(context: ContextTypes.DEFAULT_TYPE):
    if not controller.memory["monitoring"]:
        return
    for symbol in controller.memory["active_symbols"]:
        try:
            candles = fetch_klines(symbol, "1h", 200)
            patterns = detect_patterns(candles)
            for p in patterns:
                if p["confidence"] >= controller.memory["alert_threshold"]:
                    await context.bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"🤖 *Jarvis AI Alert* – {symbol}\n{p['name']} ({p['confidence']}%)",
                        parse_mode="Markdown"
                    )
                    controller.log_signal({"symbol": symbol, **p})
        except Exception as e:
            logger.warning(f"Scan failed for {symbol}: {e}")

# ===== Main Application =====
async def main():
    app = Application.builder().token(TOKEN).build()
    handlers = {
        "start": start, "help": help_cmd, "ping": ping, "scan": scan_cmd, "rsi": rsi_cmd,
        "oversee": oversee_cmd, "topmovers": topmovers_cmd, "sentiment": sentiment_cmd,
        "backtest": backtest_cmd, "predict": predict_cmd, "monitor": monitor_cmd,
        "symbols": symbols_cmd, "addsymbol": addsymbol_cmd, "removesymbol": removesymbol_cmd,
        "interval": interval_cmd, "setthreshold": setthreshold_cmd, "feedback": feedback_cmd,
        "evolve": evolve_cmd, "alerts": alerts_cmd, "logs": logs_cmd, "status": status_cmd,
        "update": update_cmd, "restart": restart_cmd
    }
    for cmd, func in handlers.items():
        app.add_handler(CommandHandler(cmd, func))
    # Background scan interval from memory
    interval = controller.memory["scan_interval_min"] * 60
    app.job_queue.run_repeating(master_scan, interval=interval, first=10)
    logger.info("🤖 Jarvis AI Overseer (full command suite) starting...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
