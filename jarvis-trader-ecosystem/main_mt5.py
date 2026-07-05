import os, sys, asyncio, logging
# Load existing main.py content
with open("main.py") as f:
    exec(f.read())
# Add MT5 status command
async def mt5status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            raise Exception("Initialize failed")
        info = mt5.account_info()
        if info is None:
            await update.message.reply_text("❌ MT5 connected but no account info.")
        else:
            await update.message.reply_text(f"✅ MT5 Connected\nBalance: {info.balance}\nEquity: {info.equity}")
        mt5.shutdown()
    except ImportError:
        await update.message.reply_text("⚠️ MT5 not available – requires Windows/macOS.")
    except Exception as e:
        await update.message.reply_text(f"❌ MT5 Error: {e}")

# Register the command
app.add_handler(CommandHandler("mt5status", mt5status))

# Re-run the bot
asyncio.run(main())
