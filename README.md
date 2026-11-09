# Jarvis Trader Ecosystem

Advanced AI-powered financial markets prediction and trading system with Telegram integration, technical/fundamental analysis support for crypto, forex and stocks.

> **Security note**: Previously committed credential files (`.env`) have been removed.  
> **You must rotate** any Telegram bot tokens and MetaTrader 5 passwords that were previously in this repository.

**Current maturity**: Level 2 (Operational tooling)  
**Active readiness work**: See branch `production-readiness` and **PRODUCTION_ROADMAP.md**

---

## Quick Status (Nov 2026)

| Item | Status |
|------|--------|
| Foundation & tooling | Complete |
| Credential rotation | **Required (blocking)** |
| Nested structure flatten | Planned (`FLATTEN.md`) |
| Paper validation | Next major phase |
| Production deploy | Only after measured paper edge |

Full plan → **[PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md)**  
Paper logging template → **[PAPER_TRADING_CHECKLIST.md](PAPER_TRADING_CHECKLIST.md)**

---

## Current Structure

The main application code currently lives inside the nested folder:

```
jarvis-trader-ecosystem/
├── jarvis-trader-ecosystem/     ← primary code (main.py, models/, docs)
├── mobile/                     ← Expo + Flutter companions
├── models/                     ← (root-level stub)
├── requirements.txt
├── .env.example
├── PRODUCTION_ROADMAP.md
├── PAPER_TRADING_CHECKLIST.md
├── START_HERE.md
└── ...
```

A flatten is planned so the real application lives at the repository root.

---

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

# 4. Configure secrets (use *rotated* tokens only)
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, etc.

# 5. Run the main application
python main.py
```

---

## Documentation Map

| File | Purpose |
|------|--------|
| **PRODUCTION_ROADMAP.md** | Single source of truth for production readiness |
| **PAPER_TRADING_CHECKLIST.md** | Daily/weekly logging + Level 3 exit criteria |
| STATUS.md | Current phase tracking |
| MATURITY.md | Honest maturity model across all repos |
| FLATTEN.md | How to remove the nested folder |
| START_HERE.md | AI upgrade overview and commands |
| Nested docs | QUICKSTART, AI_FEATURES, IMPLEMENTATION, etc. |

---

## Important Warnings

- This is a research / experimental system. Treat all signals with extreme caution.
- **Always paper-trade first** and measure results yourself.
- Never commit real `.env` files.
- Rotate any previously exposed credentials immediately.
- No repository on this account is currently at production maturity (Level 4).

---

## License

Private / experimental project. Use at your own risk.
