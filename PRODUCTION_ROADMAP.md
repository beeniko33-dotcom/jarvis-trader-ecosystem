# Production Readiness Roadmap — Jarvis Trader Ecosystem

**Last updated**: 2026-11-09  
**Current maturity**: Level 2 (Operational tooling)  
**Target**: Level 3 (Paper-validated) → Level 4 (Production)

This document is the single source of truth for bringing the entire Jarvis portfolio to a production-ready state.

---

## Guiding Principles

1. **One primary production path** — `jarvis-trader-ecosystem` is the only system we harden for real use.
2. **Paper first, always** — No live capital until *you* have measured edge over a meaningful sample.
3. **Honest maturity** — Never claim Level 3/4 until the criteria are actually met.
4. **Secret hygiene is non-negotiable**.
5. **Operational reliability > new features** at this stage.

---

## Phase 0 — Immediate Security (Do First)

- [ ] Rotate all previously exposed Telegram bot tokens
- [ ] Rotate any MetaTrader 5 / broker passwords that ever appeared in any repo
- [ ] Confirm no `.env` or secret files remain in git history of any repository
- [ ] Update local `.env` files with new credentials only
- [ ] Verify `.gitignore` is complete across all repos

**Owner**: You  
**Blocking**: Yes — nothing else should proceed until this is done.

---

## Phase 1 — Primary System Structure & Hygiene (P0)

**Repository**: `jarvis-trader-ecosystem`

### 1.1 Flatten nested structure
- [ ] Create clean branch from `production-readiness`
- [ ] Follow `FLATTEN.md` carefully (prefer `bot.py` + thin launcher approach)
- [ ] Update imports, CI workflows, and smoke tests
- [ ] Verify `python main.py --check-only` and full startup still work
- [ ] Merge only after local verification

### 1.2 Documentation accuracy
- [x] `PRODUCTION_ROADMAP.md` (this file)
- [ ] Update `STATUS.md` with current phase tracking
- [ ] Update `MATURITY.md` to reference this roadmap
- [ ] Keep `PRODUCTION.md` in sync

### 1.3 Testing foundation
- [ ] Expand smoke tests
- [ ] Add basic unit tests for predictor and memory handling
- [ ] Ensure CI stays green after flatten

---

## Phase 2 — Paper Validation (The Real Gate to Level 3)

This is the most important phase. Code completeness does not equal edge.

### 2.1 Setup
- [ ] Confirm rotated credentials are in place
- [ ] Start bot with conservative settings:
  ```
  /monitor on
  /autopilot mode conservative
  /autopilot risk low
  /setthreshold 85
  /interval 5
  ```
- [ ] Run status server in parallel
- [ ] Confirm mobile companions can reach the status API

### 2.2 Logging discipline
- [ ] Snapshot `/paperstatus` regularly
- [ ] Export or periodically archive the memory / trade log
- [ ] Track at minimum:
  - Signals generated vs executed
  - Hit rate by confidence bucket
  - Average R-multiple
  - Max drawdown
  - Performance by pair and by market regime
- [ ] Use `/feedback good|bad` where it makes sense

### 2.3 Exit criteria for Level 3
- [ ] Dozens to hundreds of closed paper trades
- [ ] Positive expectancy after realistic cost/slippage assumptions
- [ ] Performance that holds across different regimes
- [ ] You personally understand when and why the ensemble fails

**Only after these are met should live capital be considered.**

---

## Phase 3 — Production Hardening (Level 4)

### 3.1 Hosting
- [ ] Deploy bot + status server under Docker or systemd on a reliable VPS
- [ ] Auto-restart + log rotation
- [ ] Health checks and basic alerting

### 3.2 Risk controls
- [ ] Hard position size limits
- [ ] Daily loss limits
- [ ] Max open trades
- [ ] Instant kill switch (Telegram + status endpoint)
- [ ] Start with tiny live size only

### 3.3 Observability
- [ ] Structured logging improvements
- [ ] Expand status API metrics if needed
- [ ] Keep mobile companions as operational dashboard

---

## Satellite Repositories Strategy

| Repo | Action | Target State |
|------|--------|--------------|
| **jarvis-ai** | Clean + document | Secure companion (backend + mobile) |
| **jarvis-trader** | Light cleanup | Clean experimental / fallback bot |
| **jarvistrader** | Secrets hygiene only | Clean Deriv UI surface |
| **jarvis-ai-trading-system** | Redirect or archive | No further feature work |
| **quantum-peak-pro** | Freeze / archive | Skeleton only |
| **advanced-scraper** | Minimal maintenance | Authorized use only |

All satellite READMEs and PRODUCTION.md files already (or should) point to this repository as the primary path.

---

## Immediate Next Actions (This Week)

1. Complete Phase 0 (credential rotation) — **blocking**
2. Review and execute flatten on this branch
3. Begin paper trading with full logging once credentials are rotated
4. Create tracking issues for each major item

---

## Success Definition

- One clear, trustworthy production candidate (`jarvis-trader-ecosystem`)
- Measured paper edge (not claimed edge)
- Secrets never re-exposed
- All other repositories either supporting or cleanly archived
- Maturity model remains honest

---

**This roadmap supersedes scattered notes in older documentation.**  
Update this file as phases complete.
