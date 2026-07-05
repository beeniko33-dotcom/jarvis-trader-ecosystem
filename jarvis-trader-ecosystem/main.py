import os, sys, asyncio, logging, json, time, subprocess, re, random
from datetime import datetime, timedelta
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

FOREX_API = "https://api.exchangerate-api.com/v4/latest/USD"
CRYPTO_API = "https://api.coingecko.com/api/v3"
BINANCE_API = "https://api.binance.com/api/v3"

FOREX_PAIRS = [
    "EURUSD","GBPUSD","USDJPY","USDCHF","AUDUSD","NZDUSD","USDCAD",
    "EURGBP","EURJPY","GBPJPY","XAUUSD","XAGUSD","EURCHF","GBPCHF",
    "AUDJPY","NZDJPY","CADJPY","CHFJPY","EURCAD","GBPAUD"
]
FOREX_NAMES = {
    "EURUSD":"Euro/US Dollar","GBPUSD":"British Pound/US Dollar",
    "USDJPY":"US Dollar/Japanese Yen","XAUUSD":"Gold/US Dollar",
    "XAGUSD":"Silver/US Dollar"
}

MEMORY_FILE = "jarvis_memory.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE) as f: return json.load(f)
    return {
        "alert_threshold":75,"monitoring":True,
        "active_forex_pairs":["EURUSD","GBPUSD","XAUUSD","USDJPY","XAGUSD"],
        "scan_interval_min":5,"signal_history":[],
        "feedback_positive":0,"feedback_negative":0,
        "paper_trades":[],"paper_balance":1000.0,"last_evolved":None
    }
def save_memory(mem):
    with open(MEMORY_FILE,'w') as f: json.dump(mem,f,indent=2)
memory = load_memory()

class JarvisBrain:
    def __init__(self):
        self.memory = memory
    def toggle_monitoring(self, state=None):
        if state is not None: self.memory["monitoring"] = state
        else: self.memory["monitoring"] = not self.memory["monitoring"]
        save_memory(self.memory); return self.memory["monitoring"]
    def set_forex_pairs(self, pairs):
        self.memory["active_forex_pairs"] = [p.upper() for p in pairs]
        save_memory(self.memory); return self.memory["active_forex_pairs"]
    def execute_paper_trade(self, symbol, direction, confidence):
        price = get_forex_price(symbol)
        if price is None: return "❌ Could not fetch price."
        size = (self.memory["paper_balance"] * 0.1) / price
        trade = {"time":datetime.now().isoformat(),"symbol":symbol,"direction":direction,"entry":price,"size":size,"confidence":confidence,"closed":False}
        self.memory["paper_trades"].append(trade)
        save_memory(self.memory)
        return f"📝 Paper {direction.upper()} {size:.4f} {symbol.upper()} @ {price:.5f}"
    def close_paper_trade(self, idx):
        try:
            trade = self.memory["paper_trades"][idx]
            if trade["closed"]: return "Already closed."
            price = get_forex_price(trade["symbol"])
            if price is None: return "❌ Could not fetch price."
            profit = (price - trade["entry"]) * trade["size"] if trade["direction"]=="buy" else (trade["entry"] - price) * trade["size"]
            self.memory["paper_balance"] += profit
            trade.update({"closed":True,"exit":price,"profit":profit})
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
            for i,t in enumerate(open_trades):
                cur = get_forex_price(t["symbol"])
                if cur:
                    unreal = (cur - t["entry"]) * t["size"] if t["direction"]=="buy" else (t["entry"] - cur) * t["size"]
                    text += f"\n{i}: {t['symbol'].upper()} {t['direction'].upper()} @ {t['entry']:.5f} (now {cur:.5f}, P&L: ${unreal:.2f})"
        return text
    def log_signal(self, signal):
        self.memory["signal_history"].append({"time":datetime.now().isoformat(),**signal})
        save_memory(self.memory)

brain = JarvisBrain()

def get_forex_price(symbol):
    sym = symbol.upper()
    if sym in ["BITCOIN","ETHEREUM","SOLANA","BTC","ETH","SOL"]: return get_crypto_price(sym.lower())
    if sym == "XAUUSD":
        try:
            url = f"{CRYPTO_API}/simple/price?ids=gold&vs_currencies=usd"
            resp = requests.get(url, timeout=5).json()
            return float(resp["gold"]["usd"])
        except: pass
    if sym == "XAGUSD":
        try:
            url = f"{CRYPTO_API}/simple/price?ids=silver&vs_currencies=usd"
            resp = requests.get(url, timeout=5).json()
            return float(resp["silver"]["usd"])
        except: pass
    base = sym[:3]
    quote = sym[3:] if len(sym)==6 else "USD"
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        resp = requests.get(url, timeout=5).json()
        if resp.get("rates"): return 1.0/resp["rates"][quote] if base!="USD" else resp["rates"][quote]
    except: pass
    try:
        url = f"https://api.frankfurter.app/latest?from={base}&to={quote}"
        resp = requests.get(url, timeout=5).json()
        return float(resp["rates"][quote])
    except: pass
    return None

def get_crypto_price(symbol="bitcoin"):
    try:
        url = f"{CRYPTO_API}/simple/price?ids={symbol}&vs_currencies=usd"
        resp = requests.get(url, timeout=5).json()
        return float(resp[symbol]["usd"])
    except:
        try:
            sym = symbol.upper()+"USDT"
            url = f"{BINANCE_API}/ticker/price?symbol={sym}"
            resp = requests.get(url, timeout=5).json()
            return float(resp["price"])
        except: return None

def get_economic_events():
    return [
        {"time":"08:30","currency":"USD","event":"Nonfarm Payrolls","impact":"High"},
        {"time":"10:00","currency":"USD","event":"ISM Manufacturing PMI","impact":"High"},
        {"time":"14:00","currency":"USD","event":"Fed Interest Rate Decision","impact":"High"},
        {"time":"08:30","currency":"USD","event":"GDP (QoQ)","impact":"High"},
        {"time":"10:30","currency":"USD","event":"Crude Oil Inventories","impact":"Medium"}
    ]

def compute_rsi(prices, period=14):
    if len(prices) < period+1: return None
    gains = [max(prices[i]-prices[i-1],0) for i in range(1,len(prices))]
    losses = [max(prices[i-1]-prices[i],0) for i in range(1,len(prices))]
    avg_gain = sum(gains[-period:])/period
    avg_loss = sum(losses[-period:])/period
    if avg_loss==0: return 100.0
    return round(100 - (100/(1+avg_gain/avg_loss)),1)

def detect_forex_patterns(prices):
    if len(prices) < 26: return []
    ema12 = sum(prices[-12:])/12
    ema26 = sum(prices[-26:])/26
    macd = ema12 - ema26
    signal = sum(prices[-9:])/9
    prev_ema12 = sum(prices[-13:-1])/12
    prev_ema26 = sum(prices[-27:-1])/26
    prev_macd = prev_ema12 - prev_ema26
    prev_signal = sum(prices[-10:-1])/9
    alerts = []
    if prev_macd < prev_signal and macd > signal: alerts.append({"name":"MACD Bullish Cross","confidence":85})
    elif prev_macd > prev_signal and macd < signal: alerts.append({"name":"MACD Bearish Cross","confidence":85})
    change = (prices[-1]-prices[0])/prices[0]*100
    if abs(change) > 0.5: alerts.append({"name":f"Strong {'up' if change>0 else 'down'} trend","confidence":80})
    rsi = compute_rsi(prices,14)
    if rsi and rsi < 30: alerts.append({"name":"RSI Oversold","confidence":75})
    elif rsi and rsi > 70: alerts.append({"name":"RSI Overbought","confidence":75})
    return alerts

def rate_forex_setup(pair, news_sentiment=None, calendar_events=None):
    price = get_forex_price(pair)
    if price is None: return None
    score = 50
    reasons = []
    if pair in ["EURUSD","GBPUSD","AUDUSD","NZDUSD"]:
        try:
            klines = fetch_binance_klines(pair+"USDT")
            if klines:
                closes = [float(k[4]) for k in klines]
                patterns = detect_forex_patterns(closes)
                for p in patterns:
                    if p["confidence"] >= 70:
                        if "bull" in p["name"].lower(): score += 15; reasons.append(f"Bullish {p['name']}")
                        else: score -= 15; reasons.append(f"Bearish {p['name']}")
        except: pass
    if news_sentiment:
        if news_sentiment > 0.2: score += 10; reasons.append("Positive news sentiment")
        elif news_sentiment < -0.2: score -= 10; reasons.append("Negative news sentiment")
    if calendar_events:
        for e in calendar_events:
            if "USD" in e.get("currency","") and "High" in e.get("impact",""):
                if "GDP" in e.get("event","") or "NFP" in e.get("event",""):
                    score += 5 if random.random() > 0.5 else -5
                    reasons.append("High impact USD event today")
    score = max(0, min(100, score))
    return {"score":score,"reasons":reasons,"price":price}

def fetch_binance_klines(symbol="EURUSDT", interval="1h", limit=100):
    try:
        url = f"{BINANCE_API}/klines"; params = {"symbol":symbol,"interval":interval,"limit":limit}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if isinstance(data,dict) and "code" in data: return None
        return data
    except: return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 *Jarvis Forex AI* ready.\nUse /help or talk naturally.", parse_mode="Markdown")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📚 *Forex AI Commands*\n"
        "/forex – live forex rates\n/calendar – economic events\n/metals – XAUUSD / XAGUSD\n/setup <pair> – full analysis\n"
        "/mtsignal <pair> – MT5 signal\n/paperbuy /papersell <pair>\n/paperclose <idx> /paperstatus\n"
        "/scanforex – scan active pairs\n/monitor on|off\n/update – pull from GitHub\n"
        "Or say: 'forex', 'setup EURUSD', 'gold price', 'buy GBPUSD'"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower() if update.message.text else ""
    if not text: return
    if re.search(r'\b(forex|rates|currencies)\b', text):
        msg = "*Major Forex Pairs*\n"
        for pair in brain.memory["active_forex_pairs"]:
            price = get_forex_price(pair)
            if price: msg += f"{pair}: {price:.5f}\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    if re.search(r'\b(gold|xauusd)\b', text):
        price = get_forex_price("XAUUSD")
        if price: await update.message.reply_text(f"🟡 XAUUSD = ${price:.2f}")
        else: await update.message.reply_text("❌ Could not fetch.")
        return
    if re.search(r'\b(silver|xagusd)\b', text):
        price = get_forex_price("XAGUSD")
        if price: await update.message.reply_text(f"⚪ XAGUSD = ${price:.2f}")
        else: await update.message.reply_text("❌ Could not fetch.")
        return
    if re.search(r'\b(setup|analyze)\b', text):
        syms = re.findall(r'\b(eurusd|gbpusd|usdjpy|usdchf|audusd|nzdusd|usdcad|xauusd|xagusd|eurjpy|gbpjpy|eur|gbp|jpy|chf|aud|nzd|cad|gold|silver)\b', text)
        if syms:
            pair = syms[0].upper()
            if pair in ["GOLD","XAUUSD"]: pair = "XAUUSD"
            elif pair in ["SILVER","XAGUSD"]: pair = "XAGUSD"
            elif len(pair) < 6: pair = pair + "USD"
            await update.message.reply_text(f"🔍 Analyzing {pair}...")
            avg, label = get_forex_news_sentiment(pair)
            events = get_economic_events()
            rating = rate_forex_setup(pair, news_sentiment=avg, calendar_events=events)
            if rating:
                resp = f"*{pair} Setup*\nPrice: {rating['price']:.5f}\nScore: {rating['score']}/100\n"
                if rating['reasons']: resp += "\n".join(rating['reasons']) + "\n"
                if avg is not None: resp += f"News Sentiment: {label} ({avg:.2f})"
                await update.message.reply_text(resp, parse_mode="Markdown")
            else: await update.message.reply_text("❌ Could not fetch price.")
        return
    if re.search(r'\b(buy|long|paperbuy)\b', text):
        sym = re.findall(r'\b(eurusd|gbpusd|usdjpy|usdchf|audusd|nzdusd|usdcad|xauusd|xagusd|eurjpy|gbpjpy)\b', text)
        sym = sym[0] if sym else "EURUSD"
        await update.message.reply_text(brain.execute_paper_trade(sym.upper(), "buy", 80))
        return
    if re.search(r'\b(sell|short|papersell)\b', text):
        sym = re.findall(r'\b(eurusd|gbpusd|usdjpy|usdchf|audusd|nzdusd|usdcad|xauusd|xagusd|eurjpy|gbpjpy)\b', text)
        sym = sym[0] if sym else "EURUSD"
        await update.message.reply_text(brain.execute_paper_trade(sym.upper(), "sell", 80))
        return
    await update.message.reply_text("I didn't understand. Try /help or say 'forex', 'setup EURUSD', 'gold price'.")

async def ping(update, context): await update.message.reply_text("✅ Online.")
async def forex_cmd(update, context):
    msg = "*Major Forex Pairs*\n"
    for pair in brain.memory["active_forex_pairs"]:
        price = get_forex_price(pair)
        if price: msg += f"{pair}: {price:.5f}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")
async def metals_cmd(update, context):
    gold = get_forex_price("XAUUSD"); silver = get_forex_price("XAGUSD")
    msg = f"🟡 XAUUSD = ${gold:.2f}\n" if gold else ""
    msg += f"⚪ XAGUSD = ${silver:.2f}\n" if silver else ""
    await update.message.reply_text(msg or "❌ Could not fetch.")
async def calendar_cmd(update, context):
    events = get_economic_events()
    if not events: await update.message.reply_text("No high‑impact events today.")
    else:
        msg = "*High‑Impact Events*\n"
        for e in events: msg += f"• {e.get('time','')} {e.get('currency','')}: {e.get('event','')}\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
async def setup_cmd(update, context):
    pair = context.args[0].upper() if context.args else "EURUSD"
    rating = rate_forex_setup(pair)
    if rating:
        resp = f"*{pair} Setup*\nPrice: {rating['price']:.5f}\nScore: {rating['score']}/100\n"
        resp += "\n".join(rating['reasons'])
        await update.message.reply_text(resp, parse_mode="Markdown")
    else: await update.message.reply_text("❌ Could not fetch price.")
async def scanforex_cmd(update, context):
    await update.message.reply_text("🔍 Scanning active pairs...")
    for pair in brain.memory["active_forex_pairs"]:
        price = get_forex_price(pair)
        if price: await update.message.reply_text(f"{pair}: {price:.5f}")
    await update.message.reply_text("✅ Done.")
async def mt5signal_cmd(update, context):
    pair = context.args[0].upper() if context.args else "EURUSD"
    price = get_forex_price(pair)
    if price is None: await update.message.reply_text("❌ Could not fetch price."); return
    rsi = None
    if pair in ["EURUSD","GBPUSD","AUDUSD","NZDUSD"]:
        klines = fetch_binance_klines(pair+"USDT")
        if klines:
            closes = [float(k[4]) for k in klines]
            rsi = compute_rsi(closes)
    if rsi:
        if rsi < 30: direction = "BUY"; sl = round(price - 0.0020,5); tp = round(price + 0.0040,5)
        elif rsi > 70: direction = "SELL"; sl = round(price + 0.0020,5); tp = round(price - 0.0040,5)
        else: direction = "WAIT"; sl = tp = 0
    else: direction = "WAIT"; sl = tp = 0
    msg = (f"🔔 *MT5 FOREX SIGNAL*\nSymbol: {pair}\nDirection: *{direction}*\nEntry: {price:.5f}\nStop Loss: {sl:.5f}\nTake Profit: {tp:.5f}\nVolume: 0.01 lots")
    await update.message.reply_text(msg, parse_mode="Markdown")
async def paperbuy_cmd(update, context):
    sym = context.args[0].upper() if context.args else "EURUSD"
    await update.message.reply_text(brain.execute_paper_trade(sym, "buy", 80))
async def papersell_cmd(update, context):
    sym = context.args[0].upper() if context.args else "EURUSD"
    await update.message.reply_text(brain.execute_paper_trade(sym, "sell", 80))
async def paperclose_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /paperclose 0"); return
    try: await update.message.reply_text(brain.close_paper_trade(int(context.args[0])))
    except: await update.message.reply_text("Invalid index.")
async def paperstatus_cmd(update, context): await update.message.reply_text(brain.get_paper_status(), parse_mode="Markdown")
async def monitor_cmd(update, context):
    if context.args:
        state = context.args[0].lower()
        if state in ["on","true","1"]: brain.toggle_monitoring(True); await update.message.reply_text("✅ Monitoring ON.")
        elif state in ["off","false","0"]: brain.toggle_monitoring(False); await update.message.reply_text("⏸️ Monitoring OFF.")
        else: await update.message.reply_text("Usage: /monitor on|off")
    else: await update.message.reply_text(f"Monitoring {'ON' if brain.toggle_monitoring() else 'OFF'}.")
async def symbols_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /symbols eurusd gbpusd ..."); return
    brain.set_forex_pairs(context.args); await update.message.reply_text(f"✅ Active pairs: {', '.join(brain.memory['active_forex_pairs'])}")
async def addsymbol_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /addsymbol audusd"); return
    brain.memory["active_forex_pairs"].append(context.args[0].upper()); save_memory(brain.memory); await update.message.reply_text(f"✅ Added.")
async def removesymbol_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /removesymbol audusd"); return
    p = context.args[0].upper()
    if p in brain.memory["active_forex_pairs"]: brain.memory["active_forex_pairs"].remove(p); save_memory(brain.memory); await update.message.reply_text(f"✅ Removed.")
    else: await update.message.reply_text("Not in active list.")
async def interval_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /interval 10"); return
    try: mins = int(context.args[0]); brain.memory["scan_interval_min"] = mins; save_memory(brain.memory); await update.message.reply_text(f"✅ Scan interval set to {mins} min.")
    except: await update.message.reply_text("Invalid number.")
async def setthreshold_cmd(update, context):
    if not context.args: await update.message.reply_text("Usage: /setthreshold 75"); return
    try: val = int(context.args[0]); brain.memory["alert_threshold"] = val; save_memory(brain.memory); await update.message.reply_text(f"✅ Alert threshold set to {val}%")
    except: await update.message.reply_text("Invalid number.")
async def feedback_cmd(update, context):
    if not context.args or context.args[0].lower() not in ["good","bad"]: await update.message.reply_text("Usage: /feedback good|bad"); return
    is_good = context.args[0].lower() == "good"
    if is_good: brain.memory["feedback_positive"] += 1
    else: brain.memory["feedback_negative"] += 1
    save_memory(brain.memory); await update.message.reply_text("📝 Feedback recorded.")
async def evolve_cmd(update, context):
    if len(brain.memory["signal_history"]) < 5: await update.message.reply_text("Not enough data."); return
    brain.memory["last_evolved"] = datetime.now().isoformat()
    if brain.memory["feedback_negative"] > brain.memory["feedback_positive"] and brain.memory["alert_threshold"] < 95:
        brain.memory["alert_threshold"] += 2
    elif brain.memory["feedback_positive"] > brain.memory["feedback_negative"] and brain.memory["alert_threshold"] > 50:
        brain.memory["alert_threshold"] -= 2
    save_memory(brain.memory); await update.message.reply_text(f"🧬 Evolved. Threshold now {brain.memory['alert_threshold']}%")
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
    text = (f"*Jarvis Forex AI Status*\nMonitoring: {'ON' if mem['monitoring'] else 'OFF'}\nActive Pairs: {', '.join(mem['active_forex_pairs'])}\nScan interval: {mem['scan_interval_min']} min\nAlert threshold: {mem['alert_threshold']}%\nSignals: {len(mem['signal_history'])}\nFeedback: +{mem['feedback_positive']} / -{mem['feedback_negative']}\nPaper Balance: ${mem.get('paper_balance',1000):.2f} USDT\nLast evolved: {mem.get('last_evolved','never')}")
    await update.message.reply_text(text, parse_mode="Markdown")
async def update_cmd(update, context):
    await update.message.reply_text("🔄 Pulling from GitHub...")
    try:
        result = subprocess.run(["git","pull"], cwd=os.path.dirname(os.path.abspath(__file__)), capture_output=True, text=True, timeout=30)
        if result.returncode != 0: await update.message.reply_text(f"❌ Git pull failed:\n{result.stderr}"); return
        await update.message.reply_text("✅ Code updated. Restarting..."); time.sleep(1); restart_bot()
    except Exception as e: await update.message.reply_text(f"❌ Error: {e}")
async def restart_cmd(update, context): await update.message.reply_text("♻️ Restarting..."); time.sleep(1); restart_bot()

async def autonomous_cycle(context):
    if not brain.memory["monitoring"]: return
    for pair in brain.memory["active_forex_pairs"]:
        price = get_forex_price(pair)
        if price:
            patterns = []
            if pair in ["EURUSD","GBPUSD","AUDUSD","NZDUSD"]:
                klines = fetch_binance_klines(pair+"USDT")
                if klines:
                    closes = [float(k[4]) for k in klines]
                    patterns = detect_forex_patterns(closes)
            for p in patterns:
                if p["confidence"] >= brain.memory["alert_threshold"]:
                    msg = f"🤖 *Forex Alert* – {pair}\n{p['name']} ({p['confidence']}%)\nPrice: {price:.5f}"
                    await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
                    brain.log_signal({"pair":pair,**p})

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
def get_forex_news_sentiment(pair=None):
    try:
        query = "forex" if pair is None else f"{FOREX_NAMES.get(pair, pair)} forex"
        url = f"https://newsdata.io/api/1/news?apikey=pub_1234567890abcdef&q={query}&language=en"
        resp = requests.get(url, timeout=5).json()
        articles = resp.get("results",[])
        if not articles: return None, "No articles"
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
        subprocess.run(["termux-media-player","play",f.name], check=False)
        return "🔊 Alert spoken."
    except ImportError: return "gTTS not installed."
    except Exception as e: return f"Voice error: {e}"

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start)); app.add_handler(CommandHandler("help",help_cmd)); app.add_handler(CommandHandler("ping",ping))
    app.add_handler(CommandHandler("forex",forex_cmd)); app.add_handler(CommandHandler("metals",metals_cmd)); app.add_handler(CommandHandler("calendar",calendar_cmd))
    app.add_handler(CommandHandler("setup",setup_cmd)); app.add_handler(CommandHandler("mtsignal",mt5signal_cmd)); app.add_handler(CommandHandler("scanforex",scanforex_cmd))
    app.add_handler(CommandHandler("paperbuy",paperbuy_cmd)); app.add_handler(CommandHandler("papersell",papersell_cmd))
    app.add_handler(CommandHandler("paperclose",paperclose_cmd)); app.add_handler(CommandHandler("paperstatus",paperstatus_cmd))
    app.add_handler(CommandHandler("voicealert",voicealert_cmd)); app.add_handler(CommandHandler("monitor",monitor_cmd))
    app.add_handler(CommandHandler("symbols",symbols_cmd)); app.add_handler(CommandHandler("addsymbol",addsymbol_cmd)); app.add_handler(CommandHandler("removesymbol",removesymbol_cmd))
    app.add_handler(CommandHandler("interval",interval_cmd)); app.add_handler(CommandHandler("setthreshold",setthreshold_cmd))
    app.add_handler(CommandHandler("feedback",feedback_cmd)); app.add_handler(CommandHandler("evolve",evolve_cmd))
    app.add_handler(CommandHandler("alerts",alerts_cmd)); app.add_handler(CommandHandler("logs",logs_cmd)); app.add_handler(CommandHandler("status",status_cmd))
    app.add_handler(CommandHandler("update",update_cmd)); app.add_handler(CommandHandler("restart",restart_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.job_queue.run_repeating(autonomous_cycle, interval=300, first=10)
    logger.info("🤖 Jarvis Forex AI starting...")
    await app.initialize(); await app.start(); await app.updater.start_polling(); await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
