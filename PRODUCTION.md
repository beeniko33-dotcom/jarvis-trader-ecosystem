# Production Readiness – Phase 1 & Phase 2

This document tracks the path from experimental code to safer operational use.

## Phase 1 – Foundation (completed / in place)

- [x] Secrets removed from the repository tree
- [x] Strong `.gitignore`
- [x] Accurate README / START_HERE / STATUS documentation
- [x] Pinned dependencies
- [x] Root launcher that correctly starts the real application
- [x] Hardened Dockerfile (non-root user)
- [x] Basic CI (syntax / smoke)
- [x] Runtime memory and bytecode removed from version control

## Phase 2 – Next level (current target)

### Must do before any real-money use

1. **Rotate all previously exposed credentials** (Telegram bot token, MT5 password).
2. **Paper-trade for a meaningful period** (dozens to hundreds of signals) and record results.
3. **Never run autopilot with real funds** until you have verified edge yourself.
4. **Keep secrets only in environment variables / secret manager**, never in the repo.

### Operational checklist

| Item | Status | Notes |
|------|--------|-------|
| Config via `.env` only | Ready | Use `.env.example` as template |
| Non-root Docker image | Ready | See `Dockerfile` |
| Basic CI | Ready | `.github/workflows/python-ci.yml` |
| Nested structure flattened | Pending | Recommended local `git mv` |
| Automated tests | Pending | Add unit tests for predictor + memory |
| Structured logging | Partial | Logging exists; can be improved |
| Health / metrics endpoint | Not present | Bot is Telegram-only |
| Rate limiting / error recovery | Partial | Some handling exists |
| Backtest validation | Manual | Use paper trading + your own analysis |

### Recommended production settings (paper first)

```
/autopilot mode conservative
/autopilot risk low
/setthreshold 85
/interval 5
```

Start with monitoring only (`/monitor on`) before enabling autopilot.

### What “Phase 2 complete” means for this project

- Credentials rotated and never re-committed
- Bot runs reliably under Docker or a process supervisor
- Paper results recorded for at least several weeks
- You understand the real accuracy of the signals (do not trust marketing numbers)
- Nested folder either flattened or clearly documented as the source of truth

## Related systems

- **jarvis-ai** – has a more complete multi-service `docker-compose` (API, risk, DB, Redis, Traefik). Treat default passwords in that compose file as **examples only**; change them before any deployment.
- Satellite bots (`jarvis-trader`, etc.) should remain paper/experimental unless you deliberately harden them the same way.

---

**Bottom line**: Foundation is largely in place. Phase 2 is about operational discipline, credential hygiene, and verified paper performance—not just more code.
