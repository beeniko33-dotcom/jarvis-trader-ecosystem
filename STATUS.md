# Project Status – Jarvis Trader Ecosystem

**Last updated**: October 2026  
**Readiness**: Phase 1 complete · Phase 2 advanced · Smoke + status API verified

See: **PRODUCTION.md** · **MOBILE.md** · **FLATTEN.md**

## Security

- [x] Secrets removed from tree; strong `.gitignore`
- [ ] **You: rotate** previously exposed Telegram / MT5 credentials

## Engineering complete

- [x] Root launcher + pre-flight config check (`python main.py --check-only`)
- [x] Hardened Dockerfile + Python CI + `tests/test_smoke.py`
- [x] `status_server.py` — `GET /health`, `GET /status`
- [x] Expo + Flutter companions with **Live bot** metrics
- [x] Production / mobile / flatten documentation

## Verified

- Syntax: launcher, nested bot, predictor, status server
- Config check fails correctly without `.env`
- Forex public API reachable
- Status API returns paper/autopilot metrics from memory file

## Run stack

```bash
# secrets
cp .env.example .env   # rotated tokens only

# bot
python scripts/check_config.py
python main.py

# status API (same dir as jarvis_memory.json)
cd jarvis-trader-ecosystem && python status_server.py

# mobile
cd mobile/expo && npx expo start
# or: cd mobile/flutter && flutter run --dart-define=STATUS_URL=http://10.0.2.2:8787
```

## Remaining (your side)

1. Rotate credentials  
2. Paper-trade and measure real signal quality  
3. Optional structure flatten using **FLATTEN.md**  
4. EAS/store builds when you have Apple/Google accounts  
