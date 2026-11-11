import unittest
from types import SimpleNamespace

from security import is_authorized_update, parse_allowed_user_ids


def update(chat_id=None, user_id=None):
    chat = SimpleNamespace(id=chat_id) if chat_id is not None else None
    user = SimpleNamespace(id=user_id) if user_id is not None else None
    return SimpleNamespace(effective_chat=chat, effective_user=user)


class TelegramAuthorizationTests(unittest.TestCase):
    def test_exact_chat_is_allowed(self):
        self.assertTrue(is_authorized_update(update(-100123, 42), "-100123"))

    def test_other_chat_is_denied(self):
        self.assertFalse(is_authorized_update(update(-100999, 42), "-100123"))

    def test_missing_chat_configuration_fails_closed(self):
        self.assertFalse(is_authorized_update(update(-100123, 42), None))

    def test_invalid_chat_configuration_fails_closed(self):
        self.assertFalse(is_authorized_update(update(-100123, 42), "not-a-number"))

    def test_optional_user_allowlist_is_enforced(self):
        self.assertTrue(is_authorized_update(update(-100123, 42), "-100123", {42}))
        self.assertFalse(is_authorized_update(update(-100123, 43), "-100123", {42}))

    def test_empty_user_allowlist_allows_any_user_in_configured_chat(self):
        self.assertTrue(is_authorized_update(update(-100123, 43), "-100123", set()))

    def test_user_id_parser(self):
        self.assertEqual(parse_allowed_user_ids("12, 34,12"), {12, 34})
        self.assertEqual(parse_allowed_user_ids(""), set())

    def test_user_id_parser_rejects_non_numeric_values(self):
        with self.assertRaises(ValueError):
            parse_allowed_user_ids("12,abc")


if __name__ == "__main__":
    unittest.main()
