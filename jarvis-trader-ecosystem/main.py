import os, sys, asyncio, logging, json, time, subprocess, re, math
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

def restart_bot():
    os.execv(sys.executable, [sys.executable, __file__])

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

COINGECKO_API = "https://api.coingecko.com/api/v3"
BINANCE_API = "https://api.binance.com/api/v3"

# ===== Price Fetch (dual source) =====
def get_current_price(symbol="bitcoin"):
    try:
        url = f"{COINGECKO_API}/simple/price"
        resp = requests.get(url, params={"ids": symbol, "vs_currencies": "usd"}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            price = data.get(symbol, {}).get("usd")
            if price: return float(price)
    except: pass
    binance_sym = symbol.upper() if symbol.upper().endswith("USDT") else symbol.upper() + "USDT"
    try:
        url = f"{BINANCE_API}/ticker/price"
        resp = requests.get(url, params={"symbol": binance_sym}, timeout=5)
        if resp.status_code == 200:
            return float(resp.json()["price"])
    except: pass
    return None

# ===== OHLC (30 days) =====
def fetch_klines(symbol="bitcoin", days=30):
    url = f"{COINGECKO_API}/coins/{symbol}/ohlc"
    try:
        resp = requests.get(url, params={"vs_currency": "usd", "days": days}, timeout=10)
        data = resp.json()
        return [{"time": e[0], "open": e[1], "high": e[2], "low": e[3], "close": e[4], "volume": 0} for e in data]
    except:
        return []

# ===== Indicators =====
def compute_rsi(candles, period=14):
    if len(candles) < period+1: return None
    closes = [c["close"] for c in candles]
    gains = [max(closes[i]-closes[i-1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i-1]-closes[i], 0) for i in range(1, len(closes))]
    avg_gain = sum(gains[-period:])/period
    avg_loss = sum(losses[-period:])/period
    if avg_loss == 0: return 100.0
    return round(100 - (100/(1 + avg_gain/avg_loss)), 1)

def detect_patterns(candles):
    if len(candles) < 26: return []
    closes = [c["close"] for c in candles]
    ema12 = sum(closes[-12:])/12
    ema26 = sum(closes[-26:])/26
    macd = ema12 - ema26
    signal = sum(closes[-9:])/9
    prev_ema12 = sum(closes[-13:-1])/12
    prev_ema26 = sum(closes[-27:-1])/26
    prev_macd = prev_ema12 - prev_ema26
    prev_signal = sum(closes[-10:-1])/9
    alerts = []
    if prev_macd < prev_signal and macd > signal:
        alerts.append({"name":"MACD Bullish Cross","confidence":85})
    elif prev_macd > prev_signal and macd < signal:
        alerts.append({"name":"MACD Bearish Cross","confidence":85})
    change = (closes[-1]-closes[0])/closes[0]*100
    if abs(change) > 2:
        alerts.append({"name":f"Strong {'up' if change>0 else 'down'} trend","confidence":80})
    rsi = compute_rsi(candles,14)
    if rsi and rsi < 30: alerts.append({"name":"RSI Oversold","confidence":75})
    elif rsi and rsi > 70: alerts.append({"name":"RSI Overbought","confidence":75})
    return alerts

# ===== MT5 Signal Generator (pure Python, no MT5 library) =====
def generate_mt5_signal(symbol="bitcoin"):
    """Generate a trade signal with entry, SL, TP based on current price and ATR-like volatility."""
    price = get_current_price(symbol)
    if not price: return None
    candles = fetch_klines(symbol, days=7)
    if len(candles) < 20: return None
    # simple volatility: average true range over last 14 periods
    trs = []
    for i in range(1, len(candles)):
        h = candles[i]["high"]; l = candles[i]["low"]; c_prev = candles[i-1]["close"]
        trs.append(max(h-l, abs(h-c_prev), abs(l-c_prev)))
    atr = sum(trs[-14:]) / 14
    # Direction: use MACD or RSI
    rsi = compute_rsi(candles)
    if rsi and rsi < 30:
        direction = "BUY"
        sl = round(price - 2*atr, 2)
        tp = round(price + 4*atr, 2)
    elif rsi and rsi > 70:
        direction = "SELL"
        sl = round(price + 2*atr, 2)
        tp = round(price - 4*atr, 2)
    else:
        # neutral: check MACD
        closes = [c["close"] for c in candles]
        ema12 = sum(closes[-12:])/12
        ema26 = sum(closes[-26:])/26
        if ema12 > ema26:
            direction = "BUY"
            sl = round(price - 2*atr, 2)
            tp = round(price + 4*atr, 2)
        else:
            direction = "SELL"
            sl = round(price + 2*atr, 2)
            tp = round(price - 4*atr, 2)
    return {
        "symbol": symbol.upper(),
        "direction": direction,
        "entry": price,
        "sl": sl,
        "tp": tp,
        "volume": 0.01,
        "rsi": rsi
    }

# ===== AI Memory =====
MEMORY_FILE = "jarvis_memory.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE) as f: return json.load(f)
    return {
        "alert_threshold": 75, "monitoring": True,
        "active_symbols": ["bitcoin", "ethereum", "solana"],
        "scan_interval_min": 5, "signal_history": [],
        "feedback_positive": 0, "feedback_negative": 0,
        "paper_trades": [], "paper_balance": 1000.0,
        "last_evolved": None
    }
def save_memory(mem):
    with open(MEMORY_FILE, 'w') as f: json.dump(mem, f, indent=2)
memory = load_memory()

class JarvisBrain:
    def __init__(self):
        self.memory = memory
    def toggle_monitoring(self, state=None):
        if state is not None: self.memory["monitoring"] = state
        else: self.memory["monitoring"] = not self.memory["monitoring"]
        save_memory(self.memory); return self.memory["monitoring"]
    def set_symbols(self, syms):
        self.memory["active_symbols"] = [s.lower() for s in syms]
        save_memory(self.memory); return self.memory["active_symbols"]
    def execute_paper_trade(self, symbol, direction, confidence):
        price = get_current_price(symbol)
        if price is None: return "❌ Could not fetch price."
        size = (self.memory["paper_balance"] * 0.1) / price
        trade = {"time": datetime.now().isoformat(), "symbol": symbol, "direction": direction, "entry": price, "size": size, "confidence": confidence, "closed": False}
        self.memory["paper_trades"].append(trade)
        save_memory(self.memory)
        return f"📝 Paper {direction.upper()} {size:.4f} {symbol.upper()} @ ${price}"
    def close_paper_trade(self, idx):
        try:
            trade = self.memory["paper_trades"][idx]
            if trade["closed"]: return "Already closed."
            price = get_current_price(trade["symbol"])
            if price is None: return "❌ Could not fetch price."
            profit = (price - trade["entry"]) * trade["size"] if trade["direction"] == "buy" else (trade["entry"] - price) * trade["size"]
            self.memory["paper_balance"] += profit
            trade.update({"closed": True, "exit": price, "profit": profit})
            save_memory(self.memory)
            return f"💰 Closed. P&L: ${profit:.2f}. Balance: ${self.memory['paper_balance']:.2f}"
        except: return "Invalid index."
    def get_paper_status(self):
        open_trades = [t for t in self.memory["paper_trades"] if not t["closed"]]
        closed = [t for t in self.memory["paper_trades"] if t["closed"]]
        total_pnl = sum(t.get("profit",0) for t in closed)
        text = f"📊 *Paper Trading*\nBalance: ${self.memory['paper_balance']:.2f} USDT\nOpen: {len(open_trades)}\nClosed P&L: ${total_pnl:.2f}"
        if open_trades:
            text += "\n*Open:*"
            for i, t in enumerate(open_trades):
                cur = get_current_price(t["symbol"])
                if cur:
                    unreal = (cur - t["entry"]) * t["size"] if t["direction"] == "buy" else (t["entry"] - cur) * t["size"]
                    text += f"\n{i}: {t['symbol'].upper()} {t['direction'].upper()} @ {t['entry']} (now {cur}, P&L: ${unreal:.2f})"
        return text
    def log_signal(self, signal):
        self.memory["signal_history"].append({"time": datetime.now().isoformat(), **signal})
        save_memory(self.memory)

brain = JarvisBrain()

# ===== Telegram Handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 *Jarvis AI* ready.\nUse /help or just talk naturally.", parse_mode="Markdown")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📚 *Commands*\n"
        "/scan /rsi /oversee /topmovers /price <sym>\n"
        "/mtsignal <sym> – generate MT5 trade signal\n"
        "/paperbuy /papersell /paperclose /paperstatus\n"
        "/sentiment /voicealert <text>\n"
        "/monitor on|off /symbols <list> /addsymbol /removesymbol\n"
        "/interval /setthreshold /feedback good|bad /evolve /status /update"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip() if update.message.text else ""
    if not text: return
    t = text.lower()
    # Natural language parsing (abbreviated)
    if re.search(r'\b(scan|check|analyze)\b', t):
        syms = re.findall(r'\b(bitcoin|ethereum|solana|cardano|dogecoin|btc|eth|sol)\b', t)
        syms = [s.replace("btc","bitcoin").replace("eth","ethereum").replace("sol","solana") for s in syms] or brain.memory["active_symbols"]
        for sym in syms:
            candles = fetch_klines(sym, 30)
            patterns = detect_patterns(candles)
            msg = f"*{sym.upper()}*:\n" + ("\n".join([f"{p['name']} ({p['confidence']}%)" for p in patterns]) if patterns else "No patterns.")
            if 'rsi' in t:
                rsi = compute_rsi(candles)
                msg += f"\nRSI: {rsi if rsi else 'N/A'}"
            await update.message.reply_text(msg, parse_mode="Markdown")
        return
    if re.search(r'\b(buy|long|paper\s*buy)\b', t):
        sym = re.findall(r'\b(bitcoin|ethereum|solana|btc|eth|sol)\b', t)
        sym = sym[0].replace("btc","bitcoin").replace("eth","ethereum").replace("sol","solana") if sym else "bitcoin"
        await update.message.reply_text(brain.execute_paper_trade(sym, "buy", 80))
        return
    if re.search(r'\b(sell|short|paper\s*sell)\b', t):
        sym = re.findall(r'\b(bitcoin|ethereum|solana|btc|eth|sol)\b', t)
        sym = sym[0].replace("btc","bitcoin").replace("eth","ethereum").replace("sol","solana") if sym else "bitcoin"
        await update.message.reply_text(brain.execute_paper_trade(sym, "sell", 80))
        return
    if re.search(r'\b(portfolio|status|paper\s*status)\b', t):
        await update.message.reply_text(brain.get_paper_status(), parse_mode="Markdown")
        return
    if re.search(r'\brsi\b', t):
        msg = ""
        for sym in brain.memory["active_symbols"]:
            candles = fetch_klines(sym, 30)
            rsi = compute_rsi(candles)
            msg += f"{sym.upper()} RSI: {rsi if rsi else 'N/A'}\n"
        await update.message.reply_text(msg)
        return
    await update.message.reply_text("I didn't understand. Try /help or say 'scan bitcoin', 'buy ethereum', 'rsi', 'portfolio'.")

async def ping(update, context): await update.message.reply_text("✅ Online.")
async def price_cmd(update, context):
    sym = context.args[0].lower() if context.args else "bitcoin"
    price = get_current_price(sym)
    if price: await update.message.reply_text(f"💲 {sym.upper()} = ${price:.2f}")
    else: await update.message.reply_text("❌ Could not fetch price.")

async def mt5signal_cmd(update, context):
    sym = context.args[0].lower() if context.args else "bitcoin"
    sig = generate_mt5_signal(sym)
    if not sig:
        await update.message.reply_text("❌ Could not generate MT5 signal. Try /price first.")
        return
    text = (
        f"🔔 *MT5 TRADE SIGNAL*\n"
        f"Symbol: {sig['symbol']}\n"
        f"Direction: *{sig['direction']}*\n"
        f"Entry: {sig['entry']:.2f}\n"
        f"Stop Loss: {sig['sl']:.2f}\n"
        f"Take Profit: {sig['tp']:.2f}\n"
        f"Volume: {sig['volume']} lots\n"
        f"RSI(14): {sig['rsi'] if sig['rsi'] else 'N/A'}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def scan_cmd(update, context):
    await update.message.reply_text("🔍 Scanning...")
    for sym in brain.memory["active_symbols"]:
        candles = fetch_klines(sym, 30)
        patterns = detect_patterns(candles)
        for p in patterns:
            if p["confidence"] >= brain.memory["alert_threshold"]:
                await update.message.reply_text(f"⚠️ {sym.upper()}: {p['name']} ({p['confidence']}%)", parse_mode="Markdown")
    await update.message.reply_text("✅ Done.")

async def rsi_cmd(update, context):
    msg = ""
    for sym in brain.memory["active_symbols"]:
        candles = fetch_klines(sym, 30)
        rsi = compute_rsi(candles)
        msg += f"{sym.upper()} RSI: {rsi if rsi else 'N/A'}\n"
    await update.message.reply_text(msg)

async def oversee_cmd(update, context):
    await update.message.reply_text("🧠 Full AI report...")
    report = ["*Jarvis AI Market Report*"]
    for sym in brain.memory["active_symbols"]:
        candles = fetch_klines(sym, 30)
        patterns = detect_patterns(candles)
        rsi = compute_rsi(candles)
        change = (candles[-1]["close"] - candles[0]["close"]) / candles[0]["close"] * 100 if candles else 0
        report.append(f"\n*{sym.upper()}* | {change:+.2f}% | RSI: {rsi if rsi else 'N/A'}")
        for p in patterns: report.append(f"• {p['name']} ({p['confidence']}%)")
    await update.message.reply_text("\n".join(report), parse_mode="Markdown")

async def topmovers_cmd(update, context):
    movers = get_top_movers()
    msg = "📈 *Top 24h Movers*\n" + "\n".join([f"{'🟢' if ch>=0 else '🔴'} {s}: {ch:+.2f}%" for s,ch in movers])
    await update.message.reply_text(msg, parse_mode="Markdown")

async def sentiment_cmd(update, context):
    avg, label = get_news_sentiment()
    if avg: await update.message.reply_text(f"📰 Sentiment: {label} ({avg:.2f})")
    else: await update.message.reply_text(f"❌ {label}")

async def paperbuy_cmd(update, context):
    sym = context.args[0].lower() if context.args else "bitcoin"
    await update.message.reply_text(brain.execute_paper_trade(sym, "buy", 80))
async def papersell_cmd(update, context):
    sym = context.args[0].lower() if context.args else "bitcoin"
    await update.message.reply_text(brain.execute_paper_trade(sym, "sell", 80))
async def paperclose_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /paperclose 0"); return
    try: await update.message.reply_text(brain.close_paper_trade(int(context.args[0])))
    except: await update.message.reply_text("Invalid index.")
async def paperstatus_cmd(update, context): await update.message.reply_text(brain.get_paper_status(), parse_mode="Markdown")
async def voicealert_cmd(update, context):
    text = " ".join(context.args) if context.args else "Jarvis alert!"
    await update.message.reply_text(speak_alert(text))
async def monitor_cmd(update, context):
    if context.args:
        state = context.args[0].lower()
        if state in ["on","true","1"]: brain.toggle_monitoring(True); await update.message.reply_text("✅ Monitoring ON.")
        elif state in ["off","false","0"]: brain.toggle_monitoring(False); await update.message.reply_text("⏸️ Monitoring OFF.")
        else: await update.message.reply_text("Usage: /monitor on|off")
    else: await update.message.reply_text(f"Monitoring {'ON' if brain.toggle_monitoring() else 'OFF'}.")
async def symbols_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /symbols bitcoin ethereum solana ..."); return
    syms = brain.set_symbols(context.args); await update.message.reply_text(f"✅ Tracking: {', '.join(syms)}")
async def addsymbol_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /addsymbol cardano"); return
    syms = brain.add_symbol(context.args[0]); await update.message.reply_text(f"✅ Added. Now: {', '.join(syms)}")
async def removesymbol_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /removesymbol cardano"); return
    syms = brain.remove_symbol(context.args[0]); await update.message.reply_text(f"✅ Removed. Now: {', '.join(syms)}")
async def interval_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /interval 10"); return
    try: mins = int(context.args[0]); brain.adjust_interval(mins); await update.message.reply_text(f"✅ Scan interval set to {mins} min.")
    except: await update.message.reply_text("Invalid number.")
async def setthreshold_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /setthreshold 75"); return
    try: val = int(context.args[0]); brain.set_threshold(val); await update.message.reply_text(f"✅ Alert threshold set to {val}%")
    except: await update.message.reply_text("Invalid number.")
async def feedback_cmd(update, context):
    if not context.args or context.args[0].lower() not in ["good","bad"]: await update.message.reply_text("Usage: /feedback good|bad"); return
    is_good = context.args[0].lower() == "good"; brain.add_feedback(is_good)
    await update.message.reply_text(f"📝 Feedback recorded as {'positive' if is_good else 'negative'}.")
async def evolve_cmd(update, context): await update.message.reply_text(f"🧬 {brain.evolve()}")
async def alerts_cmd(update, context):
    history = brain.memory["signal_history"][-10:]
    if not history: await update.message.reply_text("No recent alerts.")
    else:
        lines = ["*Recent Alerts*"]
        for h in reversed(history): lines.append(f"• {h['time'][:16]} – {h.get('name','Signal')} ({h.get('confidence','?')}%)")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
async def logs_cmd(update, context):
    with open(MEMORY_FILE) as f: data = json.load(f)
    total = len(data["signal_history"]); pos = data["feedback_positive"]; neg = data["feedback_negative"]
    await update.message.reply_text(f"📋 *Logs*\nSignals: {total}\nPositive: {pos}\nNegative: {neg}\nThreshold: {data['alert_threshold']}%\nMonitoring: {'ON' if data['monitoring'] else 'OFF'}", parse_mode="Markdown")
async def status_cmd(update, context):
    mem = brain.memory
    text = (
        f"*Jarvis Status*\n"
        f"Monitoring: {'ON' if mem['monitoring'] else 'OFF'}\n"
        f"Symbols: {', '.join(mem['active_symbols'])}\n"
        f"Scan interval: {mem['scan_interval_min']} min\n"
        f"Alert threshold: {mem['alert_threshold']}%\n"
        f"Signals: {len(mem['signal_history'])}\n"
        f"Feedback: +{mem['feedback_positive']} / -{mem['feedback_negative']}\n"
        f"Paper Balance: ${mem.get('paper_balance',1000):.2f} USDT\n"
        f"Last evolved: {mem.get('last_evolved','never')}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
async def update_cmd(update, context):
    await update.message.reply_text("🔄 Pulling from GitHub...")
    try:
        result = subprocess.run(["git", "pull"], cwd=os.path.dirname(os.path.abspath(__file__)), capture_output=True, text=True, timeout=30)
        if result.returncode != 0: await update.message.reply_text(f"❌ Git pull failed:\n{result.stderr}"); return
        await update.message.reply_text("✅ Code updated. Restarting..."); time.sleep(1); restart_bot()
    except Exception as e: await update.message.reply_text(f"❌ Error: {e}")
async def restart_cmd(update, context): await update.message.reply_text("♻️ Restarting..."); time.sleep(1); restart_bot()

# ===== Background =====
async def autonomous_cycle(context):
    if not brain.memory["monitoring"]: return
    for sym in brain.memory["active_symbols"]:
        candles = fetch_klines(sym, 30)
        patterns = detect_patterns(candles)
        for p in patterns:
            if p["confidence"] >= brain.memory["alert_threshold"]:
                msg = f"🤖 *Jarvis AI Alert* – {sym.upper()}\n{p['name']} ({p['confidence']}%)"
                await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

# ===== Utilities =====
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
def get_news_sentiment():
    try:
        url = f"https://newsdata.io/api/1/news?apikey=pub_1234567890abcdef&q=cryptocurrency&language=en"
        resp = requests.get(url, timeout=5).json()
        articles = resp.get("results",[])
        if not articles: return None, "No articles."
        sentiments = [analyzer.polarity_scores(a["title"])["compound"] for a in articles[:5]]
        avg = sum(sentiments)/len(sentiments)
        if avg > 0.2: return avg, "Positive 😀"
        elif avg < -0.2: return avg, "Negative 😱"
        else: return avg, "Neutral 😐"
    except: return None, "Error"

def speak_alert(text):
    try:
        from gtts import gTTS
        import tempfile
        tts = gTTS(text=text, lang='en')
        f = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(f.name)
        subprocess.run(["termux-media-player", "play", f.name], check=False)
        return "🔊 Alert spoken."
    except ImportError: return "gTTS not installed."
    except Exception as e: return f"Voice error: {e}"

def get_top_movers():
    ids = ["bitcoin","ethereum","solana","cardano","dogecoin","ripple","binancecoin"]
    url = f"{COINGECKO_API}/simple/price"
    params = {"ids": ",".join(ids), "vs_currencies": "usd", "include_24hr_change": "true"}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    movers = []
    for cid, info in data.items():
        change = info.get("usd_24h_change", 0)
        movers.append((cid.upper(), change))
    movers.sort(key=lambda x: abs(x[1]), reverse=True)
    return movers[:5]

# ===== Main =====
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("price", price_cmd))
    app.add_handler(CommandHandler("mtsignal", mt5signal_cmd))
    app.add_handler(CommandHandler("scan", scan_cmd))
    app.add_handler(CommandHandler("rsi", rsi_cmd))
    app.add_handler(CommandHandler("oversee", oversee_cmd))
    app.add_handler(CommandHandler("topmovers", topmovers_cmd))
    app.add_handler(CommandHandler("sentiment", sentiment_cmd))
    app.add_handler(CommandHandler("paperbuy", paperbuy_cmd))
    app.add_handler(CommandHandler("papersell", papersell_cmd))
    app.add_handler(CommandHandler("paperclose", paperclose_cmd))
    app.add_handler(CommandHandler("paperstatus", paperstatus_cmd))
    app.add_handler(CommandHandler("voicealert", voicealert_cmd))
    app.add_handler(CommandHandler("monitor", monitor_cmd))
    app.add_handler(CommandHandler("symbols", symbols_cmd))
    app.add_handler(CommandHandler("addsymbol", addsymbol_cmd))
    app.add_handler(CommandHandler("removesymbol", removesymbol_cmd))
    app.add_handler(CommandHandler("interval", interval_cmd))
    app.add_handler(CommandHandler("setthreshold", setthreshold_cmd))
    app.add_handler(CommandHandler("feedback", feedback_cmd))
    app.add_handler(CommandHandler("evolve", evolve_cmd))
    app.add_handler(CommandHandler("alerts", alerts_cmd))
    app.add_handler(CommandHandler("logs", logs_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("update", update_cmd))
    app.add_handler(CommandHandler("restart", restart_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.job_queue.run_repeating(autonomous_cycle, interval=30, first=5)
    logger.info("🤖 Jarvis with MT5 signals starting...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
