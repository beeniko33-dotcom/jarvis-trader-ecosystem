# Production Readiness – Phase Overview

**Authoritative plan**: See **PRODUCTION_ROADMAP.md** (added November 2026).

This file remains for historical context and quick reference.

## Phase 1 – Foundation (completed)

- [x] Secrets removed from the repository tree
- [x] Strong `.gitignore`
- [x] Accurate README / START_HERE / STATUS documentation
- [x] Pinned dependencies
- [x] Root launcher that correctly starts the real application
- [x] Hardened Dockerfile (non-root user)
- [x] Basic CI (syntax / smoke)
- [x] Runtime memory and bytecode removed from version control
- [x] Production roadmap + paper trading checklist added

## Phase 2 – Current target (Operational → Paper-validated)

### Must do before any real-money use

1. **Rotate all previously exposed credentials** (Telegram bot token, MT5 password).
2. **Paper-trade for a meaningful period** and record results using `PAPER_TRADING_CHECKLIST.md`.
3. **Never run autopilot with real funds** until you have verified edge yourself.
4. **Keep secrets only in environment variables / secret manager**, never in the repo.

### Operational checklist

| Item | Status | Notes |
|------|--------|-------|
| Config via `.env` only | Ready | Use `.env.example` as template |
| Non-root Docker image | Ready | See `Dockerfile` |
| Basic CI | Ready | `.github/workflows/python-ci.yml` |
| Nested structure flattened | Pending | Follow `FLATTEN.md` |
| Automated tests | Partial | Smoke tests exist; expand later |
| Structured logging | Partial | Logging exists; can be improved |
| Health / metrics endpoint | Ready | `status_server.py` |
| Rate limiting / error recovery | Partial | Some handling exists |
| Backtest / paper validation | Manual | Use paper trading + checklist |

### Recommended paper settings

```
/autopilot mode conservative
/autopilot risk low
/setthreshold 85
/interval 5
```

Start with monitoring only (`/monitor on`) before enabling autopilot.

## Phase 3 – Production (only after Level 3)

- Reliable hosting (Docker/systemd + VPS)
- Hard risk limits + kill switch
- Observability and alerting
- Tiny live size only

## Related systems

- **jarvis-ai** – companion backend / multi-agent / mobile. Treat default secrets as examples only.
- Satellite bots (`jarvis-trader`, etc.) should remain paper/experimental unless deliberately hardened the same way.

---

**Bottom line**: Foundation is in place. The next real work is credential rotation + measured paper performance. Everything else is secondary until those two items are done.
