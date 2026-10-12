# Jarvis Trader Ecosystem — Getting Started

**Status**: Experimental research system. Use for paper trading only until thoroughly validated.

> **Security reminder**: Previously committed credential files have been removed.  
> Rotate any Telegram bot tokens and MetaTrader 5 passwords that were ever present in this repository.

## Quick Start

```bash
# 1. Clone and enter the repository
git clone https://github.com/beeniko33-dotcom/jarvis-trader-ecosystem.git
cd jarvis-trader-ecosystem

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure secrets
cp .env.example .env
# Edit .env and set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
# Also copy/create a .env inside the nested folder if needed:
# cp .env jarvis-trader-ecosystem/.env

# 5. Run the bot (root launcher starts the real application)
python main.py
```

The real application code currently lives in the nested folder `jarvis-trader-ecosystem/`.  
The root `main.py` is a launcher that correctly changes into that directory and runs it.

## Important Commands (once the Telegram bot is running)

```
/monitor on              # Enable price data collection
/autopilot on            # Enable automatic paper trading
/autopilot mode balanced
/autopilot risk medium
/mlscan                  # Scan for signals
/paperstatus             # View paper trades
/status                  # System status
```

## Documentation Map

| File | Purpose |
|------|--------|
| `STATUS.md` | Current project status, security, and next steps |
| `README.md` | High-level overview and setup |
| Nested `QUICKSTART.md` | Detailed command reference |
| Nested `AI_FEATURES.md` | How the ML components work |
| Nested `IMPLEMENTATION.md` | Architecture notes |
| Nested `UPGRADE_SUMMARY.md` / `CHANGELOG.md` | History of changes |

## Critical Warnings

1. **Paper trade first**. The system is experimental.
2. **Never commit real `.env` files**.
3. **Rotate any previously exposed credentials**.
4. Claims of high accuracy in older documentation should be treated with skepticism until you verify performance yourself.
5. The nested folder structure is technical debt; a future cleanup will flatten it.

## Related Repositories

- [jarvis-ai](https://github.com/beeniko33-dotcom/jarvis-ai) — backend / risk components
- [jarvis-trader](https://github.com/beeniko33-dotcom/jarvis-trader) — smaller RSI signal bot
- Other satellite projects exist under the same account; this repository is the primary trading bot.

---

For the full current status see **STATUS.md**.
