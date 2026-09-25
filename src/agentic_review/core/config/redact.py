"""The one function every user-visible message passes through before it is stored or printed (research R-9, SC-007)."""

from __future__ import annotations

REDACTED = "[REDACTED]"


def redact(text: str, secret: str | None) -> str:
    if not secret:
        return text
    return text.replace(secret, REDACTED)
