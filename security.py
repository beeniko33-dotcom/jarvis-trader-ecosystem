"""Telegram update authorization helpers for Jarvis.

The bot fails closed when TELEGRAM_CHAT_ID is missing or invalid.
Optionally restrict individual Telegram account IDs with
TELEGRAM_ALLOWED_USER_IDS=123456,789012.
"""
from __future__ import annotations


def parse_allowed_user_ids(raw: str | None) -> set[int]:
    """Parse a comma-separated list of Telegram numeric user IDs."""
    if not raw or not raw.strip():
        return set()
    parsed: set[int] = set()
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            value = int(item)
        except ValueError as exc:
            raise ValueError("TELEGRAM_ALLOWED_USER_IDS must contain numeric IDs only") from exc
        if value <= 0:
            raise ValueError("Telegram user IDs must be positive integers")
        parsed.add(value)
    return parsed


def is_authorized_update(update, configured_chat_id: str | None,
                         allowed_user_ids: set[int] | None = None) -> bool:
    """Return True only for the exact configured chat and optional user allowlist."""
    if not configured_chat_id:
        return False
    try:
        expected_chat_id = int(configured_chat_id.strip())
    except (AttributeError, TypeError, ValueError):
        return False

    chat = getattr(update, "effective_chat", None)
    user = getattr(update, "effective_user", None)
    if chat is None or getattr(chat, "id", None) != expected_chat_id:
        return False

    allowed = allowed_user_ids or set()
    if allowed and (user is None or getattr(user, "id", None) not in allowed):
        return False
    return True
