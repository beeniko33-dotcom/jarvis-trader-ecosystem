# Frontends across all projects

| Project | Frontend | How to open |
|---------|----------|-------------|
| **jarvis-trader-ecosystem** | Live ops dashboard + Expo/Flutter | `python status_server.py` → http://127.0.0.1:8787/ |
| **jarvis-trader** | HTML + `/status` API | `python status_server.py` → http://127.0.0.1:8788/ |
| **jarvis-ai** | Existing app UI + `frontend/ops.html` | Compose stack; open ops.html statically |
| **jarvistrader** | Next.js Deriv app | `npm install && npm run dev` |
| **advanced-scraper** | `frontend/index.html` | Open file or `python -m http.server` in `frontend/` |
| **jarvis-ai-trading-system** | `frontend/index.html` (landing) | Static page |
| **quantum-peak-pro** | `frontend/index.html` (skeleton) | Static page |

## Ports (defaults)

| Service | Port |
|---------|------|
| Ecosystem status | 8787 |
| jarvis-trader status | 8788 |
| jarvis-ai API | 8000 |
| jarvis-ai risk | 9000 |
| jarvistrader (Next) | 3000 |

## Note

One full product UI is enough for trading ops (ecosystem dashboard + mobile).
Satellite repos have honest, minimal frontends so each project is browsable without claiming full production apps.
