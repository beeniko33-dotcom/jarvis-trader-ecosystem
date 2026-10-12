# Project Status – Jarvis Trader Ecosystem

**Last updated**: October 2026  
**Readiness**: Phase 1 complete · Phase 2 in progress · Smoke tests verified

See also: **PRODUCTION.md**, **MOBILE.md**

## Security

- [x] Removed committed credential files
- [x] Strong `.gitignore` + `.env.example`
- [x] Runtime junk / bytecode removed
- [ ] **Rotate** previously exposed Telegram token and MT5 password (your action)

## Verified in automated / sandbox checks

- [x] `main.py` (launcher) parses and compiles
- [x] Nested `jarvis-trader-ecosystem/main.py` compiles (~958 lines)
- [x] `models/predictor.py` compiles (~488 lines)
- [x] `scripts/check_config.py` correctly fails when `.env` is missing
- [x] Public forex API reachable (exchangerate-api)
- [x] CI workflow runs syntax + smoke tests

Live Telegram bot start was **not** executed here (requires your rotated secrets and a host process).

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # real secrets only
python scripts/check_config.py
python tests/test_smoke.py
python main.py         # starts nested bot after config check
# or: python main.py --check-only
```

## Mobile

Expo + Flutter companion apps under `mobile/`. See **MOBILE.md**.

## Your next actions

1. Rotate credentials  
2. Run bot on your machine/VPS with paper trading  
3. Optional: flatten nested folder locally  
