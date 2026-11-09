# Maturity model (honest)

“Full maturity” for a trading stack means more than code files. It requires verified paper performance, rotated secrets, reliable hosting, and operational discipline.

**Tracking document**: See `PRODUCTION_ROADMAP.md` for the concrete plan to move levels.

## Levels

| Level | Meaning |
|-------|--------|
| **0 Skeleton** | Placeholder only |
| **1 Foundation** | Secrets hygiene, gitignore, honest docs, runnable entry |
| **2 Operational tooling** | Status API, CI smoke, dashboard, config checks |
| **3 Paper-validated** | You measured signal quality over time |
| **4 Production** | Hardened deploy, monitoring, real risk controls, no exposed defaults |

## Account map (updated 2026-11-09)

| Project | Level | Notes |
|---------|-------|-------|
| **jarvis-trader-ecosystem** | **2** | Primary path. Roadmap + paper checklist now in place. Needs credential rotation → paper validation → Level 3 |
| **jarvis-ai** | **2** (infra) | Companion backend + mobile. Clean secrets before any deploy |
| **jarvis-trader** | **1–2** | Compact experimental bot. Keep simple |
| **jarvistrader** | **1–2** | Next.js / Deriv UI surface only |
| **advanced-scraper** | **1** | Toolkit; authorized use only |
| **jarvis-ai-trading-system** | **0–1** | Sparse. Prefer primary ecosystem |
| **quantum-peak-pro** | **0** | Skeleton. Freeze or archive |

## What moves the ecosystem to Level 3–4

1. Rotate all previously exposed credentials (Phase 0)
2. Paper trade and log results for weeks using the checklist (Phase 2)
3. Host bot + status_server under systemd/Docker on a VPS (Phase 3)
4. Optional but recommended: flatten nested folder (`FLATTEN.md`)
5. Only then consider small live size with strict risk limits

**No repository on this account is currently at Level 4.**

This file remains intentionally conservative. Progress is tracked in `STATUS.md` and `PRODUCTION_ROADMAP.md`.
