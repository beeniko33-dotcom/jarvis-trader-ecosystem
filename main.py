import pandas as pd
from data.fetcher import fetch_crypto_data
from models.ta_indicators import generate_signals
from notifier.telegram_bot import send_telegram_alert
from config.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import os
from dotenv import load_dotenv

load_dotenv()

def run_analysis():
    df = fetch_crypto_data('BTC/USDT', '1h', 200)
    df = generate_signals(df)
    latest = df.iloc[-1]
    if latest['signal'] == 1:
        alert = f"🚀 **BUY Signal** for BTC/USDT at {latest['close']}\nRSI: {latest['rsi']:.2f}"
        send_telegram_alert(alert, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
        print("Buy signal sent!")
    elif latest['signal'] == -1:
        alert = f"⚠️ **SELL Signal** for BTC/USDT at {latest['close']}"
        send_telegram_alert(alert, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
        print("Sell signal sent!")

if __name__ == "__main__":
    run_analysis()
    print("JarvisTrader run complete.")