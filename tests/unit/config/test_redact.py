from __future__ import annotations

from agentic_review.core.config.redact import REDACTED, redact


def test_every_occurrence_is_replaced() -> None:
    assert redact("key=abc123 again abc123", "abc123") == f"key={REDACTED} again {REDACTED}"


def test_no_secret_leaves_text_unchanged() -> None:
    assert redact("nothing here", None) == "nothing here"
    assert redact("nothing here", "") == "nothing here"
    assert redact("nothing here", "abc123") == "nothing here"
