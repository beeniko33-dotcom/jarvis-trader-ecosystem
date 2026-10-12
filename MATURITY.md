# Maturity model (honest)

“Full maturity” for a trading stack means more than code files. It requires verified paper performance, rotated secrets, reliable hosting, and operational discipline.

## Levels

| Level | Meaning |
|-------|--------|
| **0 Skeleton** | Placeholder only |
| **1 Foundation** | Secrets hygiene, gitignore, honest docs, runnable entry |
| **2 Operational tooling** | Status API, CI smoke, dashboard, config checks |
| **3 Paper-validated** | You measured signal quality over time |
| **4 Production** | Hardened deploy, monitoring, real risk controls, no exposed defaults |

## Account map (as of Oct 2026)

| Project | Level | Notes |
|---------|-------|-------|
| **jarvis-trader-ecosystem** | **2** | Best path. Needs your paper validation → 3 |
| **jarvis-ai** | **2** (infra) | Compose stack present; change default secrets before deploy |
| **jarvis-trader** | **1–2** | Compact bot + dashboard; experimental |
| **jarvistrader** | **1–2** | Next.js UI; fill Deriv env for real use |
| **advanced-scraper** | **1** | Toolkit; authorized use only |
| **jarvis-ai-trading-system** | **0–1** | Sparse; use primary ecosystem |
| **quantum-peak-pro** | **0** | Skeleton only |

## What would move ecosystem to level 3–4

1. You rotate all previously exposed credentials  
2. Paper trade and log results for weeks  
3. Host bot + status_server under systemd/Docker on a VPS  
4. Optional: flatten nested folder (FLATTEN.md)  
5. Only then consider small live size with strict risk limits  

No repository on this account is currently at level 4.
