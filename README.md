# Jarvis Trader Ecosystem

Advanced AI-powered financial markets prediction and trading system with Telegram integration, technical/fundamental analysis support for crypto, forex and stocks.

> **Security note (Oct 2026)**: Previously committed credential files (`.env`) have been removed.  
> **You must rotate** any Telegram bot tokens and MetaTrader 5 passwords that were previously in this repository, as they were publicly visible.

## Current Structure

The main application code currently lives inside the nested folder:

```
jarvis-trader-ecosystem/
├── jarvis-trader-ecosystem/     ← primary code (main.py, models/, docs)
├── mobile/                     ← Expo + Flutter mobile stubs
├── models/                     ← (root-level stub)
├── requirements.txt
├── .env.example
├── START_HERE.md               ← detailed upgrade notes
└── ...
```

## Quick Start

```bash
# 1. Clone
git clone https://github.com/beeniko33-dotcom/jarvis-trader-ecosystem.git
cd jarvis-trader-ecosystem

# 2. Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
# or from the nested folder if needed:
# pip install -r jarvis-trader-ecosystem/requirements.txt

# 4. Configure secrets
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, etc.

# 5. Run the main application
cd jarvis-trader-ecosystem
python main.py
```

## Documentation

- `START_HERE.md` – overview of the AI upgrade and commands
- Nested folder contains: `QUICKSTART.md`, `AI_FEATURES.md`, `IMPLEMENTATION.md`, `UPGRADE_SUMMARY.md`, `CHANGELOG.md`

## Important Warnings

- This is a research / experimental system. Past documentation claims high accuracy; treat all signals with extreme caution.
- Always paper-trade first.
- Never commit real `.env` files.
- Rotate any previously exposed credentials immediately.

## License

Private / experimental project. Use at your own risk.
