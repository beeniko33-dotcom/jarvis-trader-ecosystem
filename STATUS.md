# Project Status – Jarvis Trader Ecosystem

**Last updated**: 2026-11-09  
**Current maturity**: Level 2 (Operational tooling)  
**Active branch for readiness work**: `production-readiness`

**Primary documents**:
- **PRODUCTION_ROADMAP.md** ← single source of truth for all next steps
- **PAPER_TRADING_CHECKLIST.md** ← logging template + Level 3 exit criteria
- PRODUCTION.md · MATURITY.md · FLATTEN.md · MOBILE.md

---

## Current Phase Tracking

| Phase | Status | Notes |
|-------|--------|-------|
| **Phase 0 – Security** | ⏳ In progress (blocking) | Credential rotation still required |
| **Phase 1 – Structure & Hygiene** | Ready to start | Flatten plan exists (`FLATTEN.md`) |
| **Phase 2 – Paper Validation** | Waiting on Phase 0 | Real gate to Level 3 |
| **Phase 3 – Production Hardening** | Not started | Only after measured paper edge |

---

## Security

- [x] Secrets removed from tree; strong `.gitignore`
- [ ] **You: rotate** all previously exposed Telegram bot tokens and MT5 / broker passwords
- [ ] Confirm no secrets remain in git history

---

## Engineering complete (Level 2)

- [x] Root launcher + pre-flight config check (`python main.py --check-only`)
- [x] Hardened Dockerfile + Python CI + `tests/test_smoke.py`
- [x] `status_server.py` — `GET /health`, `GET /status`
- [x] Expo + Flutter companions with Live bot metrics
- [x] Production / mobile / flatten documentation
- [x] Production roadmap + paper trading checklist added (Nov 2026)

## Verified

- Syntax: launcher, nested bot, predictor, status server
- Config check fails correctly without `.env`
- Forex public API reachable
- Status API returns paper/autopilot metrics from memory file

---

## Run stack (current)

```bash
# secrets (rotated tokens only)
cp .env.example .env

# bot
python scripts/check_config.py
python main.py

# status API
cd jarvis-trader-ecosystem && python status_server.py

# mobile
cd mobile/expo && npx expo start
# or: cd mobile/flutter && flutter run --dart-define=STATUS_URL=http://10.0.2.2:8787
```

---

## Immediate remaining work (ordered)

1. **Rotate credentials** (Phase 0 – blocking)
2. Flatten nested structure (follow `FLATTEN.md`)
3. Begin sustained paper trading using `PAPER_TRADING_CHECKLIST.md`
4. Only after measured edge → production hosting + risk controls

See **PRODUCTION_ROADMAP.md** for the full plan across the entire Jarvis portfolio.
