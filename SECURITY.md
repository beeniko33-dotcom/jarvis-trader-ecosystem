# Jarvis security notes

## Telegram access control

The bot now checks every incoming Telegram update before command or message handlers run.

- `TELEGRAM_CHAT_ID` is required and must match the exact chat ID. If it is missing or invalid, all incoming updates are denied.
- `TELEGRAM_ALLOWED_USER_IDS` is an optional comma-separated list of numeric Telegram user IDs. When set, only those users in the configured chat are allowed.
- Keep the bot token and all account credentials in an untracked `.env` file or a secret manager. Never paste tokens into issues, chats, screenshots, or commits.

Example:

```dotenv
TELEGRAM_BOT_TOKEN=replace_with_a_new_bot_token
TELEGRAM_CHAT_ID=your_numeric_chat_id
TELEGRAM_ALLOWED_USER_IDS=123456789
```

## Credential rotation is mandatory

The repository's previous Git history contained credentials. Treat every credential that was ever committed as compromised, even if the current files no longer contain it.

1. Revoke and regenerate the Telegram bot token with BotFather.
2. Change any MT5/broker passwords and API keys that were committed.
3. Update only your private deployment environment; do not commit real values.
4. Review GitHub Actions secrets and any hosting environment variables.

Removing a secret from the latest commit does not remove it from Git history and does not invalidate it.

## Trading boundary

The current autopilot implementation creates local paper trades. It does not place live broker orders. Do not enable real-money execution by assuming that paper-trade controls are equivalent to broker-side risk controls.

## Model files

Only load model/pickle artifacts from a trusted source. Python pickle files can execute code during deserialization.

## Verification

Run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q jarvis-trader-ecosystem
```

These tests validate access-control helpers and basic syntax. They do not establish profitable signals or production readiness.
