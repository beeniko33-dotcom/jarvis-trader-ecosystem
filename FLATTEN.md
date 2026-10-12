# Flatten nested folder (local checklist)

The real application currently lives under `jarvis-trader-ecosystem/` inside the repo.
Root `main.py` is a launcher. Flattening is best done **on your machine** with git.

## Before you start

```bash
git status          # must be clean
git pull origin main
cp -a jarvis-trader-ecosystem /tmp/jarvis-nested-backup
```

## Recommended approach (safe)

1. Create a branch:

```bash
git checkout -b flatten-structure
```

2. Move nested app files to root **without overwriting** critical root files:

```bash
# Core app
git mv jarvis-trader-ecosystem/main.py app_main.py   # temporary name
# After review, replace launcher or keep launcher calling app_main.py

git mv jarvis-trader-ecosystem/models models_app 2>/dev/null || true
git mv jarvis-trader-ecosystem/status_server.py status_server.py
git mv jarvis-trader-ecosystem/requirements.txt requirements.nested.txt

# Docs you want at root (optional)
# git mv jarvis-trader-ecosystem/QUICKSTART.md QUICKSTART.md
```

Because root already has `main.py`, `models/`, `requirements.txt`, and docs, prefer:

- Keep root `main.py` as launcher **or** rename nested `main.py` to `bot.py` and point the launcher at it.
- Prefer nested `models/predictor.py` over the root stub.

**Simplest production-friendly layout:**

```text
bot.py                 # former nested main.py
models/predictor.py    # real predictor
status_server.py
main.py                # thin launcher -> bot.py
requirements.txt
mobile/
scripts/
tests/
```

Example after copy:

```bash
# If git mv conflicts, use regular mv then git add
cp jarvis-trader-ecosystem/main.py bot.py
cp jarvis-trader-ecosystem/models/predictor.py models/predictor.py
cp jarvis-trader-ecosystem/status_server.py status_server.py

# Update launcher main.py to run bot.py instead of nested path
# Update imports in bot.py if needed (models.predictor stays the same if models/ is at root)

python -m py_compile bot.py models/predictor.py status_server.py main.py
python scripts/check_config.py
python tests/test_smoke.py
```

3. Remove empty nested tree when verified:

```bash
rm -rf jarvis-trader-ecosystem
git add -A
git commit -m "refactor: flatten nested application into repository root"
```

4. Test:

```bash
python main.py --check-only
# with .env set:
python main.py
python status_server.py
```

5. Merge when green:

```bash
git checkout main
git merge flatten-structure
git push
```

## Notes

- Do **not** commit `.env` or `jarvis_memory.json`.
- Mobile apps do not depend on the nested path.
- CI smoke tests look for `jarvis-trader-ecosystem/main.py` today — update `tests/test_smoke.py` and CI after flatten.

## Why not automated here

Bulk `git mv` of many files + conflict resolution needs your local git working tree. This checklist is the safe path.
